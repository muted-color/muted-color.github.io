"""Render the measured grouped bars in a compact mobile-readable composition.

Usage: python when2call-behavior-breakdown.py /path/to/render_figure.py
The installed renderer provides palette, patterns, and accessibility metadata;
this wrapper supplies explicit compact geometry because its preset is 1200px wide.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

stem = pathlib.Path(__file__).with_suffix('')
spec = json.loads(stem.with_suffix('.figure.json').read_text())
with tempfile.TemporaryDirectory() as directory:
    rendered = pathlib.Path(directory) / 'figure.svg'
    subprocess.run([sys.executable, sys.argv[1], str(stem.with_suffix('.figure.json')), str(rendered)], check=True)
    root = ET.fromstring(rendered.read_text())
ns = 'http://www.w3.org/2000/svg'
ET.register_namespace('', ns)
def tag(name):
    return '{' + ns + '}' + name
root.set('width', '780')
root.set('height', '635')
root.set('viewBox', '0 0 780 635')
root.find(tag('rect')).set('width', '780')
root.find(tag('rect')).set('height', '635')
group = root.find(tag('g'))
group.clear()
group.set('font-family', 'Arial, Helvetica, sans-serif')

def element(name, **attrs):
    return ET.SubElement(group, tag(name), {k.replace('_','-'):str(v) for k,v in attrs.items()})

def text(x, y, value, cls='', anchor='start', bold=False):
    item = element('text', x=x, y=y, font_size=26, font_weight=700 if bold else 400,
                   fill='#11120F' if bold or cls=='value-label' else '#686B66', text_anchor=anchor)
    if cls:
        item.set('class', cls)
    item.text = str(value)
    return item

text(72,60,spec['title'],'figure-title',bold=True).set('font-size','24')
styles = {'structure':('url(#bar-hatch)','#5E7FD8'), 'decision':('#D9DCD7','#686B66')}
for item,x in zip(spec['series'],[72,420]):
    fill,stroke=styles[item['id']]
    element('rect',x=x,y=96,width=24,height=18,fill=fill,stroke=stroke,stroke_width=1.4)
    text(x+36,116,item['label'],'series-label')

x0,x1,top,bottom=100,760,210,510
text(x0,174,'Correct labels / 100')
for value in spec['y_ticks']:
    y=bottom-(value-spec['y_min'])/(spec['y_max']-spec['y_min'])*(bottom-top)
    text(x0-16,y+9,value,'axis-tick','end')
for cls,coords in [('axis-y',(x0,top,x0,bottom)),('axis-x zero-line',(x0,bottom,x1,bottom))]:
    line=element('line',x1=coords[0],y1=coords[1],x2=coords[2],y2=coords[3],stroke='#11120F',stroke_width=1.5)
    line.set('class',cls)
    line.set('data-axis-id','main')
values={(item['category'],item['series']):item['value'] for item in spec['values']}
for i,category in enumerate(spec['categories']):
    center=x0+(i+.5)*(x1-x0)/3
    for j,series in enumerate(spec['series']):
        value=values[(category['id'],series['id'])]
        x=center-66+j*72
        y=bottom-value/100*(bottom-top)
        fill,stroke=styles[series['id']]
        bar=element('rect',x=x,y=y,width=60,height=bottom-y,fill=fill,stroke=stroke,stroke_width=1.4)
        bar.set('class','data-mark')
        bar.set('data-series',series['id'])
        bar.set('data-category',category['id'])
        bar.set('data-value',str(value))
        text(x+30,y-14,value,'value-label','middle')
    lines=['Unable to','answer'] if category['id']=='unable' else [category['label']]
    for k,line in enumerate(lines):
        text(center,550+32*k,line,'category-label','middle')
ET.indent(root)
stem.with_suffix('.svg').write_text(ET.tostring(root,encoding='unicode')+'\n')
