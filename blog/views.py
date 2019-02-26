from django.shortcuts import render, HttpResponse, redirect
from blog import forms, models
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib

# Create your views here.

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'POST':
        # 初始化一个给ajax返回的数据
        ret = {'status': 0, 'msg': ''}
        # 从提交过来的数据中，取到用户名和密码
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        # 获取 用户填写的验证码
        # valid_code = request.POST.get('valid_code')
        # 获取极验验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        # print(valid_code)
        print('用户输入的验证码'.center(120, '='))
        if result:
            # 验证码正确,利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                print('用户的用户名密码正确')
                # 用户名密码正确# 给用户做登录
                auth.login(request, user)
                ret['msg'] = '/index/'
            else:
                # 用户名密码错误
                print('用户的用户名密码错误')
                ret['status'] = 1
                ret['msg'] = '用户名或密码错误'
        else:
            ret['status'] = 1
            ret['msg'] = '验证码错误'
        return JsonResponse(ret)
    return render(request, 'login2.html')


# 注册的视图函数
def register(request):
    if request.method == 'POST':
        ret = {'status': 0, 'msg': ''}
        form_obj = forms.RegForm(request.POST)
        print(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop('re_password')
            avatar_img = request.FILES.get('avatar')
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret['msg'] = '/index/'
            print(ret)
            return JsonResponse(ret)
        else:
            print(form_obj.errors)
            ret['status'] = 1
            ret['msg'] = form_obj.errors
            print(ret)
            print('=' * 120)
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    print(form_obj)
    return render(request, 'register.html', {'form_obj': form_obj})


# 获取验证码图片的视图
def get_valid_img(request):
    from PIL import Image, ImageDraw, ImageFont
    import random

    # 获取随机颜色的函数
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成一个图片对象
    img_obj = Image.new(
        'RGB',
        (220, 35),
        get_random_color()
    )
    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件，得到一个字体对象
    font_obj = ImageFont.truetype('static/font/kumo.ttf', 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(1):
        u = chr(random.randint(65, 90))
        l = chr(random.randint(97, 122))
        n = str(random.randint(0, 9))

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20 + 40 * i, 0), tmp, fill=get_random_color(), font=font_obj)

    print(''.join(tmp_list))
    print('生成的验证码'.center(120, '='))
    # 不能保存到全局变量

    # 保存到session
    request.session['valid_code'] = ''.join(tmp_list)
    # 加干扰线
    # width = 220  # 图片宽度（防止越界）
    # height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=get_random_color())
    # # 加干扰点
    # for i in range(40):
    #     draw_obj.point((random.randint(0, width), random.randint(0, height)), fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    # 将生成的图片保存在磁盘上
    # with open("s10.png", "wb") as f:
    #     img_obj.save(f, "png")
    # # 把刚才生成的图片返回给页面
    # with open("s10.png", "rb") as f:
    #     data = f.read()

    # 不需要在硬盘上保存文件，直接在内存中加载就可以
    from io import BytesIO
    io_obj = BytesIO()
    # 将生成的图片数据保存在io对象中
    img_obj.save(io_obj, 'png')
    # 从io对象里面取上一步保存的数据
    data = io_obj.getvalue()
    return HttpResponse(data)


# 使用极验滑动验证码
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def login2(request):
    pass


def check_username_exist(request):
    ret = {'status': 0, 'msg': ''}
    username = request.GET.get('username')
    print('#'*100)
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret['status'] = 1
        ret['msg'] = '用户名已被注册'
    return JsonResponse(ret)
