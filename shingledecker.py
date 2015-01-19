import os
import sys

from string import Template
import flickrapi
import yaml
import micawber
import urllib2
import socket

providers = micawber.bootstrap_basic()
api = yaml.load(open('api.yaml'))
flickr = flickrapi.FlickrAPI(api['key'], api['secret'])
(token, frob) = flickr.get_token_part_one(perms='write')
if not token:
    raw_input("Press ENTER after you authorize this program")
flickr.get_token_part_two((token, frob))


def load_template(tpl):
    tpl_file = open(tpl)
    return Template(tpl_file.read())

def safe_list_get (l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

def gallery():
    set_list = flickr.photosets_getList()
    set_thumbnails = '<ul class="thumbnails">'
    for i, item in enumerate(set_list[0]):
        set_title = item[0].text
        prev_set = safe_list_get(set_list[0], (i-1), None)
        if prev_set is not None:
            prev_set_title = prev_set[0].text
        else:
            prev_set_title = None
        next_set = safe_list_get(set_list[0], (i+1), None)
        if next_set is not None:
            next_set_title = next_set[0].text
        else:
            next_set_title = None
        set_dir = "".join(x for x in set_title.replace(' ', '_') if x.isalnum() or x == '_').lower()
        if prev_set_title is not None:
            prev_set_dir = "".join(x for x in prev_set_title.replace(' ', '_') if x.isalnum() or x == '_').lower()
        else:
            prev_set_dir = None
        if next_set_title is not None:
            next_set_dir = "".join(x for x in next_set_title.replace(' ', '_') if x.isalnum() or x == '_').lower()
        else:
            next_set_dir = None
        if not os.path.exists(os.path.join('sights', set_dir)):
          os.mkdir(os.path.join('sights', set_dir))
        this_set = flickr.walk_set(item.attrib['id'])
        #print item.attrib['id']
        thumbnails = list()
        set_index_tpl = load_template('templates/sights/thumbnail_index.tpl')
        set_index = open('sights/index.html', 'w')
        set_thumbnail = '<li class="span12"><a href="/sights/%s/index.html">%s</a></li>' % (set_dir, set_title.title())
        set_thumbnails += set_thumbnail
        set_thumbnails += '</ul>'
        set_index_str = set_index_tpl.substitute({'title': 'Sights', 'thumbnail_str': set_thumbnails, 'pager': ''})
        set_index.writelines(set_index_str)
        set_index.close()

        for photo in this_set:
            photo_id = photo.get('id')
            try:
                resp = flickr.photos_getInfo(photo_id=photo_id)
                photo_url = resp[0].getchildren()[-1][0].text
            except (IndexError, urllib2.URLError) as e:
                print e
                continue
            print photo_id, photo_url, set_title
            try:
                flickr_thumbnail = micawber.extract('http://www.flickr.com/photos/davidwatson/%s/sizes/q/' %(photo_id), providers)[1]['http://www.flickr.com/photos/davidwatson/%s/sizes/q/' %(photo_id)]['thumbnail_url']
                photo_page =  micawber.extract('http://www.flickr.com/photos/davidwatson/%s/in/photostream/' % (photo_id), providers)[0][0]
                photo_url = micawber.extract('http://www.flickr.com/photos/davidwatson/%s/in/photostream/' % (photo_id), providers)[1]['http://www.flickr.com/photos/davidwatson/%s/in/photostream/' % (photo_id)]['url']
            except (socket.timeout, KeyError) as e:
                print e
                continue
            page_img = '<a href="%s" class="thumbnail"><img src="%s"></a>' % (photo_page, photo_url)
            thumbnail = '<a href="/sights/%s/%s.html" class="thumbnail"><img src="%s"></a>' % (set_dir, photo_id, flickr_thumbnail)
            page_template = load_template('templates/sights/thumbnail_index.tpl')
            page_thumbnail = '<ul class="thumbnails"><li class="span12">%s</li></ul>' % (page_img)
            page_str = page_template.substitute({'title': set_title.title(), 'thumbnail_str': page_thumbnail, 'pager': ''})
            page = open('sights/%s/%s.html' % (set_dir, photo_id), 'w')
            page.writelines(page_str)
            thumbnails.append(thumbnail)

        thumbnail_template = load_template('templates/sights/thumbnail_index.tpl')
        thumbnail_index = open('sights/%s/index.html' % (set_dir), 'w')
        thumbnail_str = ('<ul class="thumbnails">')
        for thumbnail in thumbnails:
            thumbnail_str += '<li class="span1">'
            thumbnail_str += thumbnail
            thumbnail_str += '</li>'
        thumbnail_str += '</ul>'
        if prev_set_dir is not None:
            previous = "/sights/%s/index.html" % (prev_set_dir)
        else:
            previous = "#"
        if next_set_dir is not None:
            next = "/sights/%s/index.html" % (next_set_dir)
        else:
            next = "#"
        pager = '<ul class="pager"><li><a href="%s">Previous</a></li><li><a href="%s">Next</a></li></ul>' % (previous, next)

        thumbnail_ul = thumbnail_template.substitute({'title': set_title.title(), 'thumbnail_str': thumbnail_str, 'pager': pager})
        thumbnail_index.writelines(thumbnail_ul)
        thumbnail_index.close()


def main():
    path = "posts"
    jts = load_template('templates/journal/index.tpl')
    pts = load_template('templates/journal/post.tpl')
    rts = load_template('templates/journal/row.tpl')
    jhf = open('journal/index.html', 'w')
    rows = str()
    for (path, dirs, files) in os.walk(path):
        for i, f in enumerate(files):
            pf = open(os.path.join(path, f))
            row = {'id': i,
                   'filename': f,
                   'date': pf.readline(),
                   'title': pf.readline(),
                   'content': pf.read()}
            rows += rts.substitute(**row)
            phf = open(os.path.join('journal', row['filename']), 'w')
            post = pts.substitute(**row)
            phf.writelines(post)
    jrnl_html = jts.substitute(rows=rows)
    jhf.writelines(jrnl_html)

if __name__ == '__main__':
    gallery()
    #main()
