import urllib3

#  忽略警告：InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised.
urllib3.disable_warnings()
import json
import os

# http://www.meituan.com/meishi/api/poi/getMerchantComment?id=42913246&offset=0&pageSize=50&sortType=1

COMMENT_URL = 'http://www.meituan.com/meishi/api/poi/getMerchantComment?id={}&offset={}&pageSize=50&sortType=1'

# DIVIDER = '\n' + '=' * 200 + '\n'
DIVIDER = '\n\n\n'


def repeat(func, retry=10):
    success = False
    response = None
    try:
        response = func()
        success = response.code == 200
    except:
        pass
    if not success and retry > 0:
        repeat(func, retry - 1)
    return response


def get_comment(id, offset=0, result=None, save_dir=None, sub_dir=False):
    # result = [] if result is None else result
    url = COMMENT_URL.format(id, offset)
    response = urllib3.PoolManager().request('GET', url, headers={
        'Host': 'www.meituan.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'uuid=d9f34299c1aa4700b57b.1533529950.1.0.0; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk_cuid=1650d8210c2c8-01cc48fa57f124-336b7b05-13c680-1650d8210c3c8; __mta=147110536.1533529952707.1533529952707.1533529952707.1; ci=50; client-id=4fb967a2-deb0-4c90-8408-2def9dc61c9a; oc=-3SKHsosP2d57O95hCYTmTexMhVqo4FIr5jQcztD5J5u_GXn3LjVWWou3uvfqHm4cPOGIMmgH3hNpYXXqbtqA66xGDYgxq8SWnCYIRpidQP13Wxum7XxTcrTNbJC_8r_5xlRsKULCrAWTz-CPQfr6HgZM1gLCuOpCxBnDwi_9JQ; lat=30.207471; lng=120.208933',
    })
    # response = urllib2.urlopen(request)
    # response = repeat(lambda: urllib.urlopen(request))
    if not response:
        return result
    comments = None
    try:
        text = response.data.decode()
        json_data = json.loads(text, encoding='utf-8')
        data = json_data['data']
        comments = data['comments']
    except:
        return
    if comments and result:
        result.extend(comments)

    n_comments = len(comments) if comments else 0
    if sub_dir and save_dir:
        filename = 'data.txt'
        final_save_dir = os.path.join(save_dir, str(id), '%05d_%02d' % (offset // 50, n_comments))
    else:
        final_save_dir = './'
        filename = 'comment_%d.txt' % id
    filepath = os.path.join(final_save_dir, filename)
    save_2_json(comments, filepath)
    total = data['total']

    offset += n_comments
    if offset < total - 1:
        get_comment(id, offset, result, save_dir, sub_dir)
    return result


def save_2_json(comments, save_dir):
    if not comments:
        return
    dirname = os.path.abspath(os.path.dirname(save_dir))
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(save_dir, 'a', encoding='utf-8') as f:
        for c in comments:
            # get = lambda name: (c[name].encode('utf-8')) if c[name] else ''
            get = lambda name: c[name] if c[name] else ''
            menu = get('menu')
            text = get('comment')
            if not text:
                continue
            star = c['star']
            item = 'menu = %s\nstar = %s\ntext = %s' % (menu, star / 5, text)
            f.write(item + DIVIDER)

            print(text)


def dump_comment_data(id, save_dir=None, sub_dir=False):
    save_dir = save_dir or get_root_path('data/comment')
    get_comment(id, save_dir=save_dir, sub_dir=sub_dir)


def get_root_path(relative=None):
    relative = relative or ''
    root_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root_dir, relative)


if __name__ == '__main__':
    # dump_comment_data(42913246, save_dir='data/comment')
    dump_comment_data(42913246)
    # print(get_root_path())
    # print(get_root_path('data'))
