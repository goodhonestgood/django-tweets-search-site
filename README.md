# django-tweets-search-site
## 0. 설명
설정한 사용자 이름의 트윗을 날짜별로 볼 수 있습니다.
기능
- 회원가입, 로그인
- Twitter API를 이용
- 구독할 아이디 저장
- 날짜별로 검색
- 글과 글 링크, 이미지 링크 제공

효과
- 트위터 상에서 평범한 트윗과 비슷하여 혼동이 오는 광고를 제거할 수 있습니다
- 이미지를 고화질로 빠르게 저장할 수 있습니다
- 날짜별로 올라온 트윗을 한 눈에 파악할 수 있습니다

## 1. Twitter API

```python
#Twitter API BEARER_TOKEN
#토큰은 다른 곳에서 인용하기
BEARER_TOKEN = ""

def get_tweets(names, bearer_token = BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/users/{}/tweets?max_results=5&expansions=attachments.media_keys&media.fields=url,width&tweet.fields=created_at".format(names)
    response = requests.request("GET", url, headers=headers)
    
    result=[]
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    else:
        res_json = response.json()
        #필요한 형태로 만들기
        
    return {'datas':res_json}
```

Twitter API 중에서 User Tweet Timeline by ID 부분 정리

[Twitter API v2](https://documenter.getpostman.com/view/9956214/T1LMiT5U#daeb8a9f-6dac-4a40-add6-6b68bffb40cc)

#### User Tweet Timeline by ID

설명) 요청한 사용자 ID로 지정된 단일 사용자가 작성한 가장 최근 트윗을 반환한다.

- Authorization (권한 부여)
    
    Bearer Token
    
    Bearer Token은 Twitter Developer Portal에서 만든 프로젝트에서 생성한다.
    

- params (매개변수들) 일부
    
    max_results 검색할 트윗 수 (5 ≤ max_results ≤ 100)
    
    start_time / end_time 시간 설정
    
    tweet.fields 트윗에 대한 필드 기본값 id,text 이외에 created_at을 사용함
    
    expansions 아래 user.fields,media.fields를 사용할 때 필요. attachments.media_keys 사용함
    
    user.fields 사용자 ID에 대한 필드. 기본값 id, name, username
    
    media.fields 미디어 개체에 대한 필드. 기본값 media_key, type. 이외에 url 사용함
    

#### User by Username

[Twitter API v2](https://documenter.getpostman.com/view/9956214/T1LMiT5U#288337e6-91e5-4297-bde2-cae96a549732)

```python
https://api.twitter.com/2/users/by/username/{username}?user.fields=protected
```

- @username으로 user 고유 ID 불러오기
- Authorization (권한 부여)
    
    bearer token
    
- params
    
    user.fields: Default values: id,name,username 이외에 protected 사용함
    
## 2. 장고 폼으로 동적 데이터 보내기 django form dynamic choices

### 최종 결과

```python
class DateUserForm(forms.Form):
    def __init__(self,user,*args, **kwargs): 
        super(DateUserForm, self).__init__(*args, **kwargs)
        model = SubscribeTwitter
        self.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]

    from_date = forms.DateField(label='From date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}),initial=timezone.now())
    until_date = forms.DateField(label='Until date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}), initial=timezone.now())
    selected_id = forms.ChoiceField(
                label='Selected id',
                widget=forms.RadioSelect(attrs={'class':''},),
                choices=[(352353,'dfs')],
            )
```

## 설명

1. 먼저 동적 할당을 하지 않았을 때의 코드를 보면

```python
# forms.py
class DateUserForm(forms.Form):
    from_date = forms.DateField(label='From date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}),initial=timezone.now())
    until_date = forms.DateField(label='Until date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}), initial=timezone.now())
    selected_id = forms.ChoiceField(
                label='Selected id',
                widget=forms.RadioSelect(attrs={'class':''},),
                choices=[(352353,'dfs'),(235235,'dgwg'),...],
            )
```

DateField의 경우 데이터를 1차원리스트로 표현할 수 있고

ChoiceField의 경우 선택할 데이터를 튜플로 이루어진 리스트로 표현할 수 있다.

여기서 중요한 것은 ChoiceField의 choices 값을 동적으로 할당하려는 것이다.

2. 그 다음 내가 가져오려는 데이터를 가져오는 코드를 살펴보면

현재 로그인한 사용자가 저장한 데이터를 불러오기 때문에 

filter(user=user) 이 부분에서 user라는 새로운 변수가 필요하다.

```python
model = TweetIdModel
choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]
```

3. 클래스의 생성자로 user 인수를 받는다.

```python
def __init__(self,user,*args, **kwargs): 
        model = SubscribeTwitter
        ...choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]
```

4. init 메소드 안에서 DataUserForm 클래스의 변수에 직접 접근할 수 없다. 객체가 선언되면 init 메소드가 먼저 실행되기 때문이다.
    
    또한 DataUserForm의 부모클래스forms.Form 클래스에 "특정 인스턴스가 fields를 변경하고자 할 때" 사용하는 self.fields가 init에 정의되어 있다.
    
    그래서 super().__init__() 으로 이 DataUserForm 클래스를 초기화하여 self.fields를 사용한다.(중요)
    
    그 후 아래 코드를 작성하면 정상적으로 동작할 수 있게 된다.
    

```python
def __init__(self,user,*args, **kwargs): 
        super(DateUserForm, self).__init__(*args, **kwargs) # DataUserForm의 부모클래스 forms.Form 의 __init__ 메소드를 상속받는다
        model = SubscribeTwitter
        self.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]
```

5. 다시 전체 코드를 보면
    
    selected_id의 choices= [(352353,'dfs')] 이 부분은 최종적으로 클래스의 생성자에 의해 동적으로 할당된 값으로 새롭게 쓰여질 것이다.
    

```python
class DateUserForm(forms.Form):
    def __init__(self,user,*args, **kwargs): 
        super(DateUserForm, self).__init__(*args, **kwargs)
        model = SubscribeTwitter
        self.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]

    from_date = forms.DateField(label='From date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}),initial=timezone.now())
    until_date = forms.DateField(label='Until date', widget=forms.SelectDateWidget(years=YEAR_CHOICES,attrs={'class':'form-control'}), initial=timezone.now())
    selected_id = forms.ChoiceField(
                label='Selected id',
                widget=forms.RadioSelect(attrs={'class':''},),
                choices=[(352353,'dfs')],
            )
```

번외) 

1. int(o['tw_id']) 라고 쓴 이유

model을 정의할 때 분명 IntegerField로 정의했는데도 그냥 o['tw_id']로 하면 문자열이 된다

왜 데이터베이스에 숫자형으로 저장되어 있지 않은건지 아니면 불러올때 문자형으로 바뀐건지는 모르겠지만 여기서 에러가 한번 났다.

```python
self.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]
```

2. 실패한 방법

```python
form.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in list(model.objects.filter(user=user).values())]
```

이렇게 비슷하게 views.py에서 작성하여 다시 form을 넘기는 코드를 작성하면 html 파일에 값을 넘기는 것이기 때문에 실행했을때 보이기는 하지만 에러가 난다
