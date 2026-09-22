// Native, editable PowerPoint evidence deck derived from the frozen report manifest.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DEPS = process.env.CODEX_ARTIFACT_DEPENDENCIES ?? '/Users/nry/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL = process.env.CODEX_PRESENTATIONS_SKILL ?? '/Users/nry/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
const { Presentation, PresentationFile } = await import(pathToFileURL(path.join(DEPS, 'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')));
const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')));
const TMP = path.join(ROOT, '.artifact-build/presentation');
const OUTPUT = path.join(ROOT, 'output/presentation/ncaa_shot_selection.pptx');
const C = { navy:'#102A43', teal:'#087F8C', orange:'#D77A38', cream:'#FAF8F2', muted:'#526777', light:'#E6ECEF' };
const FONT = resolvePresentationFont({ fontFamily:'Arial' });
const ppt = Presentation.create({slideSize:{width:1280,height:720}});
const notes = [];

function text(slide, copy, x, y, width, height, size=28, color=C.navy, bold=false) {
  const t=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width,height},fill:'none',line:{fill:'none',width:0}});
  t.text=copy;
  t.text.style={typeface:FONT,fontSize:size,color,bold,autoFit:'none',verticalAlignment:'top'};
  return t;
}

function slide(title, bodyNotes, dark=false) {
  const s=ppt.slides.add();
  s.background.fill=dark?C.navy:C.cream;
  if(title) text(s,title,72,50,1136,104,44,dark?'#FFFFFF':C.navy,true);
  const n=ppt.slides.items.length;
  text(s,`NCAA Division I men's basketball`,72,670,800,22,16,dark?'#B7CDD5':C.muted);
  text(s,String(n).padStart(2,'0'),1160,670,45,22,16,dark?'#B7CDD5':C.muted);
  s.speakerNotes.textFrame.setText(bodyNotes);
  notes.push({slide:n,title:title || 'NCAA shot selection',notes:bodyNotes});
  return s;
}

function table(s,headers,rows,opts={}) {
  const {x=72,y=175,w=1136,h=350,widths}=opts;
  const values=[headers,...rows].map(row=>row.map(String));
  const t=s.tables.add({rows:values.length,columns:headers.length,left:x,top:y,width:w,height:h,
    values,...(widths?{columnWidths:widths}:{})});
  t.styleOptions={headerRow:true,bandedRows:false};
  t.borders.assign({fill:C.light,width:0.5,style:'solid'});
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:headers.length}).assign({
    fill:C.cream,textStyle:{typeface:FONT,fontSize:23,color:C.navy},
    margins:{left:12,right:12,top:10,bottom:10},anchor:'center'});
  t.cells.block({row:0,column:0,rowCount:1,columnCount:headers.length}).assign({
    fill:C.navy,textStyle:{typeface:FONT,fontSize:23,color:'#FFFFFF',bold:true}});
  return t;
}

function chart(s,type,config) {
  return null;
}

function image(s,file,x,y,w,h) {
  // Evidence figures are statistical results supplied by the Python pipeline.
  return fs.readFile(path.join(ROOT,'output/figures',file)).then(bytes=>s.images.add({
    blob:new Uint8Array(bytes),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain'}));
}

async function build(m) {
  let s=slide('',m.notes[0],true);
  text(s,'NCAA shot selection',72,172,1136,92,64,'#FFFFFF',true);
  text(s,"Probability estimates and constrained\nshot-mix scenarios",76,296,1030,130,38,'#DBE9EA');
  text(s,'Division I men’s basketball\nAcademic study and interactive portfolio',76,500,1050,80,26,'#B7CDD5');

  s=slide('Study population',m.notes[1]);
  table(s,['Season ending','Source attempts','Included attempts','Games','D1 teams'],m.cohort_rows,
    {y:185,h:280,widths:[235,240,240,180,241]});
  text(s,m.cohort_caption,76,505,1124,90,26,C.muted);

  s=slide('Chronological study design',m.notes[2]);
  text(s,m.split_labels[0],76,190,335,55,38,C.teal,true);
  text(s,m.split_labels[1],475,190,335,55,38,C.teal,true);
  text(s,m.split_labels[2],875,190,335,55,38,C.teal,true);
  text(s,m.split_descriptions[0],76,270,325,210,30);
  text(s,m.split_descriptions[1],475,270,325,210,30);
  text(s,m.split_descriptions[2],875,270,325,210,30);
  text(s,m.split_caveat,76,560,1125,72,25,C.muted);

  s=slide('Held-out probability performance',m.notes[3]);
  table(s,['Model',`Brier score`, 'Log loss'],m.model_rows,
    {y:180,h:300,widths:[676,230,230]});
  text(s,m.model_caption,76,525,1120,92,27,C.muted);

  s=slide('Where shots occur and what they are worth',m.notes[4]);
  await image(s,m.maps_figure,62,160,1156,405);
  text(s,m.maps_caption,76,582,1125,65,24,C.muted);

  s=slide('Calibration and uncertainty',m.notes[5]);
  chart(s,'scatter',{
    position:{left:65,top:175,width:690,height:440},
    series:[
      {name:'Predicted vs observed',xValues:m.calibration.map(x=>x.predicted),values:m.calibration.map(x=>x.observed),
        marker:{symbol:'circle',size:9},line:{fill:C.teal,width:2}},
      {name:'Perfect calibration',xValues:[0,1],values:[0,1],marker:{symbol:'none',size:0},line:{fill:C.muted,width:1.2}}
    ],scatterOptions:{style:'lineWithMarkers'},hasLegend:false,
    xAxis:{min:0,max:1,majorUnit:0.2,numberFormatCode:'0%',title:'Predicted make probability',textStyle:{fontSize:20,fill:C.muted}},
    yAxis:{min:0,max:1,majorUnit:0.2,numberFormatCode:'0%',title:'Observed make rate',textStyle:{fontSize:20,fill:C.muted},majorGridlines:{fill:C.light,width:1}}
  });
  text(s,m.uncertainty_headline,805,194,394,100,33,C.teal,true);
  text(s,m.uncertainty_body,805,320,390,269,27);

  s=slide(m.scenario_title,m.notes[6]);
  chart(s,'bar',{
    position:{left:65,top:174,width:750,height:415},
    categories:m.zone_mix.map(x=>x.zone),
    series:[
      {name:'Current mix',values:m.zone_mix.map(x=>x.current),fill:C.navy},
      {name:'Scenario mix',values:m.zone_mix.map(x=>x.proposed),fill:C.teal}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:80},hasLegend:true,
    legend:{position:'bottom',textStyle:{fontSize:22,fill:C.navy}},
    xAxis:{textStyle:{fontSize:19,fill:C.muted}},
    yAxis:{min:0,max:Math.ceil(Math.max(...m.zone_mix.flatMap(x=>[x.current,x.proposed]))*10)/10+.1,
      majorUnit:0.1,numberFormatCode:'0%',textStyle:{fontSize:20,fill:C.muted},majorGridlines:{fill:C.light,width:1}}
  });
  text(s,m.scenario_gain,855,198,340,88,48,C.teal,true);
  text(s,'modeled points\nper 100 attempts',855,295,340,100,29);
  text(s,m.scenario_interval,855,426,340,95,24,C.muted);
  text(s,m.scenario_caption,76,594,1125,59,22,C.muted);

  s=slide('Sensitivity to the movement budget',m.notes[7]);
  chart(s,'bar',{
    position:{left:65,top:178,width:755,height:420},
    categories:m.sensitivity.map(x=>x.label),
    series:[{name:'Modeled gain',values:m.sensitivity.map(x=>x.gain),fill:C.teal}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:130},hasLegend:false,
    xAxis:{title:'Maximum total share reassigned',textStyle:{fontSize:21,fill:C.muted}},
    yAxis:{min:0,title:'Modeled points per 100 attempts',textStyle:{fontSize:21,fill:C.muted},majorGridlines:{fill:C.light,width:1}},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:22,fill:C.navy}}
  });
  text(s,'The constraints\nshape the answer',866,207,338,105,32,C.teal,true);
  text(s,m.sensitivity_caption,866,349,338,244,27);

  s=slide('What this study supports',m.notes[8],true);
  text(s,m.conclusion,76,193,1125,160,38,'#FFFFFF');
  text(s,m.boundary,76,404,1110,116,29,'#B7CDD5');
  text(s,'Reproducible analysis, interactive explorer, report and editable evidence deck',76,582,1110,56,22,'#B7CDD5');
}

await fs.mkdir(TMP,{recursive:true});
await fs.mkdir(path.dirname(OUTPUT),{recursive:true});
const manifest=JSON.parse(await fs.readFile(path.join(ROOT,'.artifact-build/report_manifest.json'),'utf8'));
await build(manifest);
const candidate=path.join(TMP,'candidate.pptx');
await (await PresentationFile.exportPptx(ppt)).save(candidate);
await finalizePresentation({
  workspaceDir:ROOT,candidatePath:candidate,finalPath:OUTPUT,
  pythonExecutable:path.join(DEPS,'python/bin/python3'),
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  explicitTotalSlideCount:9,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,
  receiptPath:path.join(TMP,'validation.json'),
});
await fs.writeFile(path.join(ROOT,'docs/presentation_script.md'),
  '# Presentation script\n\nNine slides, approximately 6-7 minutes.\n\n'+notes.map(n=>`## ${n.slide}. ${n.title}\n\n${n.notes}\n`).join('\n'));
console.log(OUTPUT);
