import requests
from django.utils.timezone import datetime
from django.shortcuts import render, redirect
from .models import SubscribeTwitter
from .forms import DateUserForm, NameForm
from secret import BEARER_TOKEN

# 홈 html 렌더링
def home(request):
    return render(request, "tweets/home.html")


# 지정한 twitter id의 tweets 가져오기
def get_tweets(names, start, end, bearer_token=BEARER_TOKEN):
    start_time = start.isoformat() + "T00:00:00Z"
    end_time = end.isoformat() + "T23:59:59Z"

    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    url = "https://api.twitter.com/2/users/{}/tweets?max_results=15&start_time={}&end_time={}&expansions=attachments.media_keys,author_id&media.fields=url,width&tweet.fields=created_at&user.fields=username".format(
        names, start_time, end_time)
    response = requests.request("GET", url, headers=headers)
    # result = {datetime.date(2021, 9, 4): [{'id':'',},{'id':'',},{'id':'',},...],datetime.date()...}
    result = {}
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    elif response.json()['meta']['result_count'] == 0:
        print(response.json())
    else:
        res_json = response.json()
        print(res_json)
        for rj in res_json['data']:
            created_datetime = datetime.strptime(rj['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
            if created_datetime.date() not in result.keys():
                result[created_datetime.date()] = []
            if created_datetime.date() in result.keys():
                result[created_datetime.date()].append({
                    'id': 'https://twitter.com/{}/status/{}'.format(res_json['includes']['users'][0]['username'],
                                                                    rj['id']),
                    'media_keys': rj['attachments']['media_keys'] if 'attachments' in rj.keys() else [],
                    'text': rj['text'],
                    'created_at': created_datetime,
                    'url': [],
                })

        num = 0
        for created_date, values in result.items():
            for r in range(len(values)):
                a = num
                for i in range(len(values[r]['media_keys'])):
                    if res_json['includes']['media'][a + i]['type'] == 'photo':
                        result[created_date][r]['url'].append(
                            res_json['includes']['media'][a + i]['url'] + '?name=large')
                    num += 1
        print(result)
    return result

# twitter_feed html 가져오기 또는 form 보내기 후 get_tweets 함수 실행
def twitter_feed(request):
    if request.method == "POST":
        form = DateUserForm(request.user, request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            if form.cleaned_data['from_date'] <= form.cleaned_data['until_date']:  # 잘못된 날짜 설정
                result = get_tweets(form.cleaned_data['selected_id'], form.cleaned_data['from_date'],
                                    form.cleaned_data['until_date'])
                return render(request, "tweets/twitter_feed.html",
                              {'form': DateUserForm(request.user), 'datas': result, 'result_keys': result.keys(),
                               'date': {'from_date': form.cleaned_data['from_date'],
                                        'until_date': form.cleaned_data['until_date']}})
            else:
                return render(request, "tweets/twitter_feed.html", {'form': form, 'error': '※ Until Date가 더 커야합니다.'})
    elif request.method == "GET":
        if request.user.is_authenticated:  # 로그인 했을 때
            form = DateUserForm(request.user)
        else:
            return render(request, "common/login.html")
    return render(request, "tweets/twitter_feed.html", {'form': form})


# 구독설정 - twitter id를 찾아서 데이터베이스에 저장
def get_userID(username, bearer_token=BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    url = "https://api.twitter.com/2/users/by/username/{}?user.fields=protected,description".format(username)
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    else:
        print(response.json())
        print(response.json()['data']['id'])
        return int(response.json()['data']['id'])

def get_twname(request):
    if request.method == "POST":
        form = NameForm(request.POST)
        model = SubscribeTwitter
        if form.is_valid():
            tweet_id = get_userID(form.cleaned_data['tw_username'])
            query_list = [a['tw_id'] for a in list(model.objects.filter(user=request.user).values())]
            if tweet_id not in query_list:
                print(tweet_id)
                print(query_list)
                usernameForm = form.save(commit=False)
                usernameForm.user = request.user
                usernameForm.tw_id = tweet_id
                usernameForm.save()
                return redirect("/")
            else:
                return render(request, "tweets/subscribe.html",
                              {'form': form, 'errors': {'already_username': '이미 구독하고 있습니다.'}})
    elif request.method == "GET":
        if request.user.is_authenticated:  # 로그인 했을 때
            form = NameForm()
        else:
            return render(request, "common/login.html")
    return render(request, "tweets/subscribe.html", {'form': form})