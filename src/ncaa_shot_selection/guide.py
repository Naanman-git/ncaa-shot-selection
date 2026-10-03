"""Searchable, contextual explanations for first-time visitors."""
from __future__ import annotations
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import re
import unicodedata
from .guide_catalog import BY_KEY, SECTIONS, TOPICS, Topic

STOP_WORDS = frozenset('a an the what whats is are was were does do did can could would should i me my we you it its this that these those mean means meaning explain explanation understand tell about please how why read use work works on in of for and with'.split())


def normalize(value: str) -> str:
    value = unicodedata.normalize('NFKD', value).casefold().replace('%', ' percent ').replace('ρ', ' rho ')
    return ' '.join(re.findall(r'[a-z0-9]+', value))


def search_topics(query: str, limit: int = 8) -> list[Topic]:
    """Rank reviewed explanations; never invent an answer to an unknown term."""
    raw = normalize(query)
    terms = [w for w in raw.split() if w not in STOP_WORDS]
    if not terms:
        return [entry for entry in TOPICS if raw and any(normalize(alias) == raw for alias in (entry.title, *entry.aliases))][:limit]
    tokens = set(terms)
    compact = ''.join(terms)
    ranked = []
    for index, entry in enumerate(TOPICS):
        best = 0.0
        for alias in (entry.title, *entry.aliases):
            name = normalize(alias)
            # Do not turn "how to use" into the basketball abbreviation TO.
            if len(compact) < 4 and name.replace(' ', '') != compact:
                continue
            words = [w for w in name.split() if w not in STOP_WORDS]
            alias_tokens = set(words)
            reduced = ''.join(words)
            if raw == normalize(alias) or compact == reduced:
                best = max(best, 100)
            elif tokens <= alias_tokens:
                best = max(best, 70 + 15 * len(tokens) / max(len(alias_tokens), 1))
            elif len(alias_tokens) >= 2 and alias_tokens <= tokens:
                best = max(best, 65 + 15 * len(alias_tokens) / len(tokens))
            # Short IDs such as TO and OR need exact matches, not fuzzy ones.
            elif len(compact) >= 4 and len(reduced) >= 4:
                ratio = SequenceMatcher(None, compact, reduced).ratio()
                if ratio >= .80:
                    best = max(best, 50 + 15 * ratio)
        if not best and len(tokens) >= 2:
            body = set(normalize(entry.meaning + ' ' + entry.details).split())
            if tokens <= body:
                best = 30
        if best:
            ranked.append((best, index, entry))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return [entry for _, _, entry in ranked[:limit]]


@dataclass
class GuideContext:
    label: str
    season: int
    summary: dict
    evaluation: dict = field(default_factory=dict)
    scenario: dict = field(default_factory=dict)
    minimum: int = 5
    visible: int = 0
    outside: int = 0
    mean_probability: float = 0.0
    team_label: str = ''
    team_totals: dict = field(default_factory=dict)
    profile_label: str = ''
    profile_summary: dict = field(default_factory=dict)


def season_label(year: int) -> str:
    return f'{year - 1}–{str(year)[-2:]}'


def selection_example(key: str, context: GuideContext) -> str | None:
    """Label the correct population and units before explaining actual values."""
    s = context.summary
    scope = f'**{context.label} · {season_label(context.season)}**'
    count, games = s.get('count', 0), s.get('games', 0)
    examples = {
        'tour': f'Your shot view is {scope}: **{count:,} attempts** across **{games:,} games**. Start with Court explorer, then check Model validation.',
        'filters': f'The main shot cards, court maps and scenario currently describe {scope}. Other pages state their own selection rules.',
        'attempts': f'For {scope}, **{count:,}** is the number of recorded field-goal attempts, including makes and misses.',
        'games': f'For {scope}, **{games:,}** counts different covered game IDs rather than attempts or both teams\' participation counts.',
        'makes': f'For {scope}, **{round(s.get("fg_pct", 0) * count):,}** of **{count:,}** recorded attempts were made.',
        'fg': f'For {scope}, **{s.get("fg_pct", 0):.1%}** means about **{100 * s.get("fg_pct", 0):.1f} makes per 100 attempts** at the observed rate. This excludes free throws.',
        'observed-pps': f'For {scope}, **{s.get("observed_pps", 0):.3f}** means about **{100 * s.get("observed_pps", 0):.1f} actual field-goal points per 100 attempts** at this sample\'s average rate.',
        'predicted-pps': f'For {scope}, **{s.get("expected_pps", 0):.3f}** corresponds to **{100 * s.get("expected_pps", 0):.1f} predicted field-goal points per 100 attempts** like those recorded, under the frozen model.',
        'probability': f'For {scope}, the mean predicted make chance is **{context.mean_probability:.1%}** across recorded attempts. Individual shots can have different probabilities.',
        'map': f'The displayed court contains **{context.visible:,}** attempts from {scope}. **{context.outside:,}** outside this drawing remain in the main totals. The prediction-map minimum is **{context.minimum}** per cell.',
        'minimum': f'Your minimum is **{context.minimum} attempts per cell**. Cells below it are blank on the two prediction maps; the count map and top totals retain them.',
        'support': f'The overall shot selection is {scope}: **{count:,} attempts in {games:,} games**. Zone support must be read separately; a large total does not imply every zone is well supported.',
        'gap': f'For the main selection {scope}, observed minus predicted points per attempt is **{s.get("observed_pps", 0) - s.get("expected_pps", 0):+.3f}**. Player development\'s review prompt uses its independently selected profile and zone.',
        'player-development': f'Player development currently uses **{context.profile_label}**: **{context.profile_summary.get("count", 0):,} attempts in {context.profile_summary.get("games", 0):,} games**. Its profile selector is independent of the sidebar player choice.',
        'trend': f'The game trend currently belongs to **{context.profile_label} · {season_label(context.season)}**, with **{context.profile_summary.get("games", 0):,} recorded games**. Recent windows use up to five of those games.',
    }
    if key in examples:
        return examples[key]
    e = context.evaluation
    if key in {'validation', 'brier', 'log-loss', 'calibration', 'baseline', 'training'} and e:
        label = f'**{season_label(int(e["season"]))} full evaluation dataset**'
        if key == 'brier':
            detail = f'Mean Brier score is **{e["brier"]:.4f}**, the average squared probability error over **{int(e["n"]):,} attempts**. It is not a shooting percentage.'
        elif key == 'log-loss':
            detail = f'Mean log loss is **{e["log_loss"]:.4f}**, the average penalty for the actual results over **{int(e["n"]):,} attempts**. Lower is better on the same shots.'
        else:
            detail = f'The selected model is **{e["model"]}**. It has Brier **{e["brier"]:.4f}** and log loss **{e["log_loss"]:.4f}** over **{int(e["n"]):,} attempts**.'
        return f'For the {label}: {detail} The sidebar team and player do not change these results.'
    if key in {'scenario', 'gain', 'interval', 'mix', 'scenario-ep', 'feasible'}:
        r = context.scenario
        if not r:
            return f'The main scenario is unavailable for {scope}; at least 100 attempts are needed to show its controls.'
        if not r.get('feasible'):
            return f'For {scope}, the current scenario is unavailable: {r.get("message", "The selected limits cannot all be satisfied.")} No valid scoring gain is reported.'
        return (f'For {scope}, your current settings estimate **{r["current_ep"]:.3f} → {r["recommended_ep"]:.3f} points per attempt**, '
                f'or **{r["gain_per100"]:+.1f} points per 100 attempts**. Its conditional 95% interval is '
                f'**{r["gain_low"]:+.1f} to {r["gain_high"]:+.1f}**. These assume unchanged zone efficiencies.')
    if key in {'context', 'possession', 'possession-rate', 'ft', 'fta', 'turnovers', 'rebounds', 'team-games', 'designation'}:
        t = context.team_totals
        if not t or t.get('possessions', 0) <= 0:
            return 'No reconciled team context is available for this team and season. Shot statistics remain a separate view.'
        return (f'Team context uses **{context.team_label} · {season_label(context.season)}**, regardless of the sidebar player. '
                f'It covers **{int(t["games"]):,} team-games**, **{t["possessions"]:,.1f} estimated possessions**, '
                f'and **{t["points"] / t["possessions"]:.3f} points per estimated possession**. '
                f'It includes **{int(t["free_throws"]):,} free-throw points** and '
                f'**{100 * t["turnovers"] / t["possessions"]:.1f} turnovers per 100 estimated possessions**.')
    return None


def guide_markdown() -> str:
    """Use the same catalog for both the sidebar and the offline reference."""
    lines = ['# CourtSense beginner\'s guide', '', f'{len(TOPICS)} explanations of the interface and downloadable field names.', '',
             'The interactive guide also shows examples from your current selection. This download contains general explanations and worked examples, not live-filtered values.', '']
    for section in SECTIONS:
        lines.extend([f'## {section}', ''])
        for entry in TOPICS:
            if entry.section != section:
                continue
            lines.extend([f'### {entry.title}', '', entry.meaning, '', '**Example:** ' + entry.example, '',
                          '**More detail:** ' + entry.details, '', '**Also called / searchable fields:** ' + '; '.join(entry.aliases), '',
                          '**Related:** ' + '; '.join(BY_KEY[key].title for key in entry.related), ''])
    return '\n'.join(lines)


def _set_query(st, query: str) -> None:
    st.session_state['guide_search'] = query


def render_beginner_guide(st, context: GuideContext) -> None:
    st.subheader('Understand the numbers')
    st.caption(f'{len(TOPICS)} plain-language explanations. Search a label, abbreviation, exported field or question.')
    query = st.text_input('Find a term or ask what it means', placeholder='What does fg_pct mean?', key='guide_search').strip()
    if query:
        st.button('Clear search', key='guide_clear', on_click=_set_query, args=(st, ''))
    else:
        a, b = st.columns(2)
        a.button('FG%', key='guide_quick_fg', on_click=_set_query, args=(st, 'fg_pct'), width='stretch')
        b.button('PPS', key='guide_quick_pps', on_click=_set_query, args=(st, 'pps'), width='stretch')
        a.button('Model accuracy', key='guide_quick_validation', on_click=_set_query, args=(st, 'model validation'), width='stretch')
        b.button('Sample support', key='guide_quick_support', on_click=_set_query, args=(st, 'sample support'), width='stretch')
    entry = None
    if query:
        matches = search_topics(query)
        if not matches:
            st.info('I couldn’t find that term in the guide. Try a label from the page, an abbreviation such as FG%, or a question such as “what is log loss?”. You can also clear the search and browse by page.')
            for key in ('tour', 'probability', 'possession', 'validation'):
                st.button(BY_KEY[key].title, key=f'guide_suggestion_{key}', on_click=_set_query, args=(st, BY_KEY[key].title))
        else:
            ids = [entry.key for entry in matches]
            if len(ids) == 1:
                selected = ids[0]
            else:
                st.caption(f'{len(matches)} relevant explanations. Closest match first.')
                selected = st.selectbox('Matching explanation', ids, format_func=lambda key: BY_KEY[key].title, key=f'guide_match_{normalize(query)}')
            entry = BY_KEY[selected]
    else:
        section = st.selectbox('Browse by page or topic', ['Start here', *SECTIONS], key='guide_section')
        ids = ['tour'] if section == 'Start here' else [entry.key for entry in TOPICS if entry.section == section]
        selected = ids[0] if len(ids) == 1 else st.selectbox('Choose an explanation', ids, format_func=lambda key: BY_KEY[key].title, key=f'guide_browse_{section}')
        entry = BY_KEY[selected]
    if entry:
        st.markdown(f'### {entry.title}')
        st.markdown(entry.meaning)
        current = selection_example(entry.key, context)
        if current:
            with st.container(border=True):
                st.markdown('**On your screen**')
                st.markdown(current)
        st.markdown('**A simple example**')
        st.markdown(entry.example)
        with st.expander('More detail & how to interpret it'):
            st.markdown(entry.details)
            st.caption('Also called: ' + '; '.join(entry.aliases))
        if entry.related:
            st.caption('Keep learning')
            for key in entry.related:
                st.button(BY_KEY[key].title, key=f'guide_related_{entry.key}_{key}', on_click=_set_query, args=(st, BY_KEY[key].title))
    st.divider()
    st.download_button('Download the complete guide', guide_markdown(), file_name='CourtSense_beginner_guide.md', mime='text/markdown', key='guide_download', width='stretch')
    st.caption('Search retrieves reviewed explanations. The download includes all topics, examples and field-name aliases for offline reading.')
