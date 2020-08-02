from flask import Flask, render_template, request, jsonify, redirect
from crawler  import *


class CustomFlask(Flask):
    """防止jinja2与vue模板出现冲突"""
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))


app = CustomFlask(__name__, template_folder='page', static_folder='static')


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/ip/')
def ip():
    """获取1条ip的接口"""
    res = GenerateEffectiveIp()
    spiders = SpiderIp()
    i_ip, a_ip = res.len_pool()
    # 没有可用ip则向池中添加ip，并筛选ip
    if not a_ip:
        # 添加
        spiders.find_ip(1, 51)
        # 筛选
        res.get_ip()
    ip = res.client.spop('ip:available_ip')

    return ip


@app.route('/ip/<int:num>/')
def list_ip(num):
    """获取一定数量的ip"""
    res = GenerateEffectiveIp()
    spiders = SpiderIp()
    i_ip, a_ip = res.len_pool()
    if a_ip < num:
        spiders.find_ip(1, 51)
        res.get_ip()
    ip_list = list()
    for i in range(num):
        ip = res.client.spop('ip:available_ip')
        if ip is None:
            break
        ip_list.append(ip)

    # 返回列表
    return ip_list


@app.route('/len/')
def len_ip():
    """获取池中ip以及可用ip的数量"""
    res = MyBase()
    i_ip, a_ip = res.len_pool()
    return i_ip, a_ip


@app.route('/init/')
def init():
    """初始化(delete)可用ip"""
    res = MyBase()
    res.clear()
    _, a_ip = res.len_pool()
    if a_ip is None:
        return '初始化成功！！！'
    else:
        return '初始化失败！！！'


@app.route('/spiders/', methods=['GET', 'POST'])
def spider():
    """爬虫接口"""
    if request.method == 'POST':
        start = int(request.form.get('start'))
        end = int(request.form.get('end'))
        ss = SpiderIp()
        # 爬取指定页码的数据,添加到池中
        ss.find_ip(start, end)
        return redirect('/spiders/')

    return render_template('add_ip.html')


@app.route('/aip/')
def aip():
    """可用ip页面"""
    return render_template('available_ip.html')


@app.route('/available/', methods=['GET', 'POST'])
def available():
    """可用ip数据接口"""
    res = MyBase()
    # 获取全部内容
    _, ip_set = res.select()
    # ip数量
    length = len(ip_set)
    ip_list = list()
    # 解码bytes,并添加到list中
    for i in ip_set:
        ip_list.append(i.decode('utf-8'))

    return jsonify({'ip_list': ip_list, 'length': length, 'all_list': []})


@app.route('/iip/')
def iip():
    """代理池页面"""
    return render_template('initial_ip.html')


@app.route('/pool/', methods=['GET', 'POST'])
def pool():
    """代理池页面数据接口"""
    res = MyBase()
    ip_set, _ = res.select()
    ip_list = list()
    length = len(ip_set)
    for i in ip_set:
        ip_list.append(i.decode('utf-8'))

    return jsonify({'ip_list': ip_list, 'length': length, 'all_list': []})


@app.route('/sip/')
def sip():
    """筛选ip页面"""
    return render_template('screen_ip.html')


@app.route('/screen/', methods=['GET', 'POST'])
def screen():
    """筛选ip接口"""
    ip = GenerateEffectiveIp()
    if request.method == 'GET':
        a_ip, i_ip = ip.len_pool()
        return jsonify({'i_ip': i_ip, 'a_ip': a_ip})
    if request.method == 'POST':
        try:
            ip.get_ip()
        except Exception as e:
            print(e)
            return jsonify({'message': 0})
        # 筛选成功返回1,失败返回0
        return jsonify({'message': 1})


@app.route('/explain/')
def explain():
    """接口说明页面"""
    return render_template('explain.html')