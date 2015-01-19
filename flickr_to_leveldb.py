import flickrapi
import yaml

from string import Template
from level_dict import LevelJsonDict


api = yaml.load(open('api.yaml'))
flickr = flickrapi.FlickrAPI(api['key'], api['secret'])
(token, frob) = flickr.get_token_part_one(perms='write')
if not token:
    raw_input("Press ENTER after you authorize this program")
flickr.get_token_part_two((token, frob))
db = LevelJsonDict('flickr_photos')


def gallery():
    set_list = flickr.photosets_getList()
    for i, item in enumerate(set_list[0]):
        set_title = item[0].text
        this_set = flickr.walk_set(item.attrib['id'])
        print 'set: ', i+1, 'http://www.flickr.com/photos/davidwatson/sets/' + item.attrib['id']
        db[item.attrib['id']] = [dict(photo.items()) for photo in this_set]

def load_template(tpl):
    tpl_file = open(tpl)
    return Template(tpl_file.read())

def view():
    a = 0
    f = open('sets.txt').readlines()
    for i, (k,v) in enumerate(db.items()):
        carousel_tpl = load_template('templates/sights/carousel.html')
        id = f[i][f[i].rfind('/'):-1]
        try:
            next_id = f[i+1][f[i+1].rfind('/'):-1]
            next_set = '/sights%s.html' % (next_id)
        except:
            next_set = '/sights%s.html' % f[0][f[0].rfind('/'):-1]
        try:
            prev_id = f[i-1][f[i-1].rfind('/'):-1]
            prev_set = '/sights%s.html' % (prev_id)
        except:
            prev_set = '/sights%s.html' % f[0][f[0].rfind('/'):-1]
        carousel = open('sights' + id + '.html', 'w')
        set_url = f[i][10:]
        items = []
        for j, l in enumerate(v):
            item_tpl = load_template('templates/sights/item.html')
            ind_tpl = load_template('templates/sights/individual.html')
            title = l['title']
            id = l['id']
            try:
                next_id = v[j+1]['id']
                next_pic = '/sights/%s.html' % (next_id)
            except:
                next_pic = '/sights/%s.html' % v[0]['id']
            try:
                prev_id = v[j-1]['id']
                prev_pic = '/sights/%s.html' % (prev_id)
            except:
                prev_pic = '/sights/%s.html' % v[0]['id']
            individual = open('sights/%s.html' %(id), 'w')
            photo_url = 'http://www.flickr.com/photos/davidwatson/' + id
            src_square = 'http://farm%s.staticflickr.com/%s/%s_%s_%s.jpg' % (l['farm'], l['server'], l['id'], l['secret'], 'q')
            src_large = 'http://farm%s.staticflickr.com/%s/%s_%s_%s.jpg' % (l['farm'], l['server'], l['id'], l['secret'], 'z')
            items.append(item_tpl.substitute({'id': id, 'src': src_square}))
            individual.writelines(ind_tpl.substitute({'title': title, 'href': photo_url, 'src': src_large, 'next_pic': next_pic, 'prev_pic': prev_pic}))
        carousel.writelines(carousel_tpl.safe_substitute({'items': ''.join(items), 'title': title, 'prev_set': prev_set, 'next_set': next_set}))
        a += len(v) - 1

if __name__ == '__main__':
    #gallery()
    view()
