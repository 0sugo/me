# from nltk import word_tokenize

import hashlib
import json
import threading
from functools import partial
from string import Template

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import auth
from django.shortcuts import render

# from users.utils import word_return, se_arch
v = 0


def signup(request):
    if request.method == "GET":
        return render(request, r"signup.html", {})
    else:
        print("no prob")
        dict_signup = dict(request.POST)
        print(dict_signup)
        username = dict_signup['USERNAME'][0]
        age = dict_signup['AGE'][0]
        email = dict_signup['EMAIL'][0]
        print(email)
        email = str(email)
        if email.__contains__("."):
            name = email
            first_name = email.split()[0]
        else:
            first_name = email.split("@")[0]
        password1 = hashlib.pbkdf2_hmac(
            'sha256', email.encode(), dict_signup["PASS1"][0].encode(), 7777).hex()
        password2 = hashlib.pbkdf2_hmac(
            'sha256', email.encode(), dict_signup["PASSWORD2"][0].encode(), 7777).hex()

        if not password1 == password2:
            messages.info(request, "PASSWORD MISMATCH")
            return render(request, r"signup.html",
                          {"AGE": age, "USERNAME": username, "EMAIL": email,
                           "PASS1": "",
                           "PASSWORD2": ""})
        else:
            print(password1, password2)
            try:
                User = get_user_model()

                user = User.objects.create_user(user_name=username, first_name=name, age=age,
                                                email=email,
                                                password=password1, unique=password1)

                user.set_password(password1)
                user.save()

                link_verification = settings.SERVER + f"/user/activate/{user.unique}"
                # link_verification="https://sustainability.google/commitments/?utm_source=googlehpfooter&utm_medium=housepromos&utm_campaign=bottom-footer&utm_content="
                print(link_verification)
                t = threading.Thread(target=partial(
                    sendmail, request, email, link_verification))
                t.start()

            except Exception as e:
                print(e)
                messages.info(request, "EMAIL ALREADY EXISTS")
                return render(request, r"signup.html",
                              {"INSTITUTION": "", "COURSE": "", "GROUP": "", "EMAIL": "", "PASS1": "", "PASSWORD2": ""})
            else:

                messages.info(
                    request, "LOGIN TO YOUR SUCCESSFULLY CREATED AN ACCOUNT")
                return render(request, r"login.html", {name: name})


def test(request):
    global v
    v += 1
    return render(request, r"test.html", {"counter": v})
    # email validation
    # internet error
    # fireBase


def logout(request):
    auth.logout(request)
    messages.info(request, "Successfully logged out")
    return render(request, "base.html")


# Create your views here.
def profile(request):
    if request.method == "GET":
        if request.user.is_authenticated:

            return render(request, r"profile.html")

        else:

            return render(request, r"login.html", {"redirect": "profile"})
    else:
        user = request.user
        print("no prob")
        dict_signup = dict(request.POST)
        print(dict_signup)
        first_name = dict_signup["FIRST_NAME"][0]
        age = dict_signup['AGE'][0]
        username = dict_signup['USERNAME'][0]

        email = dict_signup['EMAIL'][0]
        password1 = hashlib.pbkdf2_hmac(
            'sha256', email.encode(), dict_signup["PASS1"][0].encode(), 7777).hex()
        password2 = hashlib.pbkdf2_hmac(
            'sha256', email.encode(), dict_signup["PASSWORD2"][0].encode(), 7777).hex()

        if not password1 == password2:
            messages.info(request, "PASSWORD MISMATCH")
            return render(request, r"profile.html")
        else:
            print(password1, password2)

            user.user_name = username
            user.first_name = first_name
            user.age = age
            user.email = email
            user.unique = password1
            user.set_password(password1)
            user.save()

            messages.info(
                request, " SUCCESSFULLY CHANGED YOUR ACCOUNT")
            return render(request, r"base.html")


def login(request):
    if request.method == "GET":
        return render(request, r"login.html", {})
    else:
        print("no prob")
        dict_signup = dict(request.POST)
        print(dict_signup)
        email = dict_signup['EMAIL'][0]
        print(email)
        email = str(email)
        print(dict_signup["PASS1"][0])
        password1 = hashlib.pbkdf2_hmac(
            'sha256', email.encode(), dict_signup["PASS1"][0].encode(), 7777).hex()
        print(password1)
        for u in get_user_model().objects.all():
            if u.email == email:
                if u.unique == password1:
                    user = u
                else:
                    user = None
            else:
                user = None

        if user is not None:
            auth.login(request, user)
            request.user = user
            messages.info(request, "SUCCESFULLY LOGGED IN")
            return render(request, f"{request.POST['redirect']}.html")
        else:
            messages.info(request, "INVALID CREDENTIALS")
            return render(request, "login.html")


def reset_link_gen(request):
    if request.method == "GET":
        return render(request, "reset_link_gen.html")
    else:
        email = dict(request.POST)["EMAIL"][0]
        with open(str(settings.BASE_DIR) + r"\reset.json", "r") as f:
            f = json.load(f)
            link = settings.SERVER + f"/user/password_reset/{email}"
            if f["reset_links"].__contains__(email):
                messages.info("Check your email")
                t = threading.Thread(target=email_send_reset, args=[request, email, link])
                t.start()
            else:
                f["reset_links"].append(email)

                t = threading.Thread(target=email_send_reset, args=[request, email, link])
                t.start()
                messages.info(request, "A reset email has been sent")
        with open(str(settings.BASE_DIR) + r"\reset.json", "w") as w:
            json.dump(f, w)
        t = threading.Thread(target=partial(
            email_send_reset, request, email, link))
        t.start()
        return render(request, "base.html")


def password_reset(request, email):
    print(email)
    user = get_user_model()
    found = False
    with open(str(settings.BASE_DIR) + r"\reset.json", "r") as f:
        f = json.load(f)
        email_list = f["reset_links"]
        if email in email_list:
            f["reset_links"].remove(email)
            for u in user.objects.all():
                print(u.unique)

                if u.email == email:
                    print(True)
                    u.set_password(hashlib.pbkdf2_hmac(
                        'sha256', email.encode(), b"0000", 7777).hex())
                    u.unique = hashlib.pbkdf2_hmac(
                        'sha256', email.encode(), b"0000", 7777).hex()
                    found = True
                    print("changed")

                    print(u.password)
                    u.save()
                    break
            if not found:
                messages.info(request, "Account not found")
                with open(str(settings.BASE_DIR) + r"\reset.json", "w") as w:
                    json.dump(f, w)
                return render(request, "base.html")
            else:
                with open(str(settings.BASE_DIR) + r"\reset.json", "w") as w:
                    json.dump(f, w)
                return render(request, "password-reset.html")

        else:
            messages.info(request, "Email cannot be reset")
            with open(str(settings.BASE_DIR) + r"\reset.json", "w") as w:
                json.dump(f, w)
            return render(request, "base.html")


def email_send_reset(request, email, link):
    t = Template("""<html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sara</title>
    <style>
        body {
            background: rgb(112, 41, 99);
        }

        div {
            color: rgb(143, 214, 156);
            text-align: center;
            font-size: 300%;
        }

        a {
            margin: 0 auto;
        }

        button {
            background: rgb(143, 214, 156);
            color: rgb(112, 41, 99);
            border: 4px solid white;
            border-radius: 49px;
            margin: 0 auto;
        }
    </style>
    </head>

    <body>
    <div>
        Click the link below <br />To rest your account  <br /> With Sara
    </div>
    <div class="button">
        <a href=$link>
            <button><h1>RESET</h1></button>
        </a>
    </div>


    </body>

    </html>

    """)

    link_verification = link
    print(email)
    message = t.substitute({"link": f"{link_verification}"})
    msg = EmailMultiAlternatives(
        'Subject',
        f"Reset your password with this link {link_verification}",
        settings.EMAIL_HOST_USER,
        [email],
    )
    msg.attach_alternative(message, "text/html")
    # Main content is now text/html
    msg.send()
    messages.info(request, "Mail successfully sent")


r"""
def record(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, r"record.html", {})
        else:
            return render(request, r"login.html", {"redirect": "login"})
    else:

        file = request.FILES["file"]

        transcribes = request.POST["transcript"]
        import datetime
        dict_signup = dict(request.POST)
        unit = dict_signup["unit"][0]
        topic = dict_signup["topic"][0]
        # unit
        # topic
        print(unit, topic)
        user = request.user
        print(user.institution)
        print(datetime.date.today())
        test_path = r"{}".format(settings.MEDIA_ROOT)
        file_path = test_path + f"\{user.institution}\{user.course + user.group}\{unit}\{str(datetime.date.today())}\{topic}\{user.unique}"
        print(file_path)
        # test_path=f"{settings.BASE_DIR}\{}\{user.course}+{user.group}{unit}{datetime.date.today()}{user.id}
        topic = dict_signup['topic'][0]
        di = {
            "unit": unit,
            "topic": topic,
            "day": datetime.date.today(),
            "files": file_path,
            "classmates": [u for u in get_user_model().objects.all() if
                           (u.institution + u.course + u.group) == (user.institution + user.course + user.group)]

        }
        test_path += f"\{user.unique}.csv"
        if os.path.exists(test_path):
            print("exists")
            p = pd.read_csv(test_path, index_col=[0])
            print(len(p.values))
            i = int(len(p.values))
            dis = pd.DataFrame(di, index=[i])
            p = pd.concat([p, dis])
            print(p.head())

            p.to_csv(test_path)
        else:
            os.makedirs(pathlib.Path(test_path).parent, exist_ok=True)
            p = pd.DataFrame(di, index=[0])
            p.to_csv(test_path)

        if not os.path.exists(file_path):
            os.makedirs(file_path)
        fss = FileSystemStorage(location=file_path)
        s = fss.save(file.name, file)
        url = fss.url(s)
        with open(file_path + r"\record.txt", "w") as f:
            f.write(transcribes)
        # threading.Thread(target=mainner, args=[transcribes, file_path, unit, topic]).start()
        # silence_based_conversion(os.path.join(file_path, "record.wav"))
        return JsonResponse({"status": url})


def ty(request, unit):
    with open(str(settings.BASE_DIR) + r"\main.json", "r") as f:
        j = json.load(f)

        if j[request.user.unique]:
            d = j[request.user.unique]

        else:
            j[request.user.unique] = {}
            d = j[request.user.unique]
        if d[unit]:
            messages.info(request, "unit already exist")
        else:
            d[unit] = {"lessons": [], "assignments": [], "cats": []}
    with open(str(settings.BASE_DIR) + r"\main.json", "r") as f:
        json.dump(j, f)


def notes(request, pk=None):
    user = request.user
    file_path = f"{settings.BASE_DIR}" + r"\records" + f"\{user.unique}.csv"
    p = pd.read_csv(file_path)
    v = len(p.values)

    p = p.iloc[int(pk)]
    print(type(p))
    print(p.files)
    url = str(p.files).split(r"C:\Users\Admin\Desktop\SOMA\records")[-1]
    url = request._current_scheme_host + "/media" + url + r"/record.wav"
    with open(p.files + r"\record.txt", "r") as f:
        notes = f.read()
        notes = nltk.word_tokenize(notes)
    with open(p.files + r"\results.json") as f:
        j = json.load(f)
        imgs = []
        google = []
        youtube = []
        classmates = []
        for i in j.keys():
            imgs.extend([j[i]["images"][val] for val in j[i]["images"].keys()])
            _ = [google.append([j[i]["google"][val], val]) for val in j[i]["google"].keys()]

            youtube.extend([val.split("?v=")[1] for val in j[i]["youtube"]])
        for _ in (notes):
            classmates.append([[f"love{y}", y] for y in range(4)])

    counter = [i for i in range(len(notes) + 1)]
    return render(request, "notes.html",
                  {"notes": notes, "counter": counter, "other_pics": imgs,
                   "articles": google, "classmates": classmates, "videos": youtube, "url": url, "pk": pk})

    # url to  download the html file for notes


def silence_based_conversion(filepath):
    # open the audio file stored in
    # the local system as a wav file.

    # open a file where we will concatenate
    # and store the recognized text
    from pathlib import Path
    p = str(Path(filepath).parent)
    print(os.path.isfile(p + r"\recognized.txt"))

    try:
        os.makedirs(p + r"\recognized.txt")
    except:
        pass
    fss = FileSystemStorage(location=p)

    fh = ""
    # split track where silence is 0.5 seconds
    # or more and get chunks
    chunks = split_on_silence(AudioSegment.from_file(filepath),
                              # must be silent for at least 0.5 seconds
                              # or 500 ms. adjust this value based on user
                              # requirement. if the speaker stays silent for
                              # longer, increase this value. else, decrease it.
                              min_silence_len=500,

                              # consider it silent if quieter than -16 dBFS
                              # adjust this per requirement
                              silence_thresh=-16
                              )

    # create a directory to store the audio chunks.
    try:
        os.mkdir('audio_chunks')
    except FileExistsError:
        pass

    # move into the directory to
    # store the audio files.
    os.chdir('audio_chunks')

    i = 0
    # process each chunk
    for chunk in chunks:

        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)

        # add 0.5 sec silence to beginning and
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent

        # export audio chunk and save it in
        # the current directory.
        print("saving chunk{0}.wav".format(i))
        # specify the bitrate to be 192 k
        audio_chunk.export("./chunk{0}.wav".format(i), bitrate='192k', format="wav")

        # the name of the newly created chunk
        filename = 'chunk' + str(i) + '.wav'

        print("Processing chunk " + str(i))

        # get the name of the newly created chunk
        # in the AUDIO_FILE variable for later use.
        file = filename

        # create a speech recognition object
        r = sr.Recognizer()

        # recognize the chunk
        with sr.AudioFile(file) as source:
            # remove this if it is not working
            # correctly.
            r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source)

        try:
            # try converting it to text
            rec = r.recognize_google(audio_listened)
            # write the output to the file.
            fh += rec + ". "

        # catch any errors.
        except sr.UnknownValueError:
            print("Could not understand audio")
            fh += "couldn't_understand"

        except sr.RequestError as e:
            print("Could not request results. check your internet connection")

        i += 1
    print(fh)
    with open(p + "recog.txt", "w") as f:
        f.write(fh)


def edit_cred(request):
    if request.method == "GET":
        return render(request, r"create_cred.html")
    else:
        dict_cred = request.POST
        spliter = "|"
        unit = request.POST["unit"]

        details = request.POST.getlist("details")
        print(details)

        for d in details:
            day = d.split(spliter)[-2]
            ty_pe = d.split(spliter)[0]  # "Assignment","Lesson""Cat"
            timelines = d.split(spliter)[-1] + " " + day
            topics = d.split(spliter)[1]
            ref = db.reference("/")

            test_path = f"{settings.BASE_DIR}\data_users\{request.user.unique}.csv"

            di = {
                "type": ty_pe,
                "unit": unit,
                "topic": topics,
                "timeline": timelines,
                "day": day,

            }
            if os.path.exists(test_path):
                print("exists")

                p = pd.read_csv(test_path, index_col=[0])
                print(len(p.values))
                i = int(len(p.values))
                dis = pd.DataFrame(di, index=[i])
                p = pd.concat([p, dis])
                print(p.head())
                print(ty_pe, timelines, topics)
                p.to_csv(test_path)

            else:
                os.makedirs(pathlib.Path(test_path).parent, exist_ok=True)

                p = pd.DataFrame(di, index=[0])
                print(p.head())

                p.to_csv(test_path)
                user = request.user

                # type $name
                # time
                # day
                # topic
                #
                ref.child("root").child(user.unique).child(unit).child(ty_pe).child("timelines").set(timelines)
                ref.child("root").child(user.unique).child(unit).child(ty_pe).child("topics").set(topics)

        messages.info(request, "Submitted successfully")
        return render(request, "base.html")


def create_cred(request):
    print("called")
    if request.method == "POST":
        unit = request.POST["unit"]
        return render(request, r"edit_cred.html", {"unit": unit})
    else:
        return render(request, "create_cred.html")

"""


def activate(request, unique):
    user = get_user_model()
    found = False
    print(user.objects.all())
    try:
        u = user.objects.filter(unique=unique)
    except:
        messages.info(request, "Account not found")
    else:

        print(u.is_active)
        if u.is_active:
            messages.info(request, "Account already activated")
        else:
            u.is_active = True
            u.save()
    finally:
        return render(request, "base.html")


from django.core.mail import EmailMultiAlternatives


def sendmail(request, email, link):
    t = Template("""<html lang="en">
<head>
<meta charset="UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Sara</title>
<style>
    body {
        background: rgb(112, 41, 99);
    }

    div {
        color: rgb(143, 214, 156);
        text-align: center;
        font-size: 300%;
    }

    a {
        margin: 0 auto;
    }

    button {
        background: rgb(143, 214, 156);
        color: rgb(112, 41, 99);
        border: 4px solid white;
        border-radius: 49px;
        margin: 0 auto;
    }
</style>
</head>

<body>
<div>
    Thank you for creating<br /> An account with Sara <br /> Click button below to activate
</div>
<div class="button">
    <a href=$link>
        <button><h1>ACTIVATE</h1></button>
    </a>
</div>


</body>

</html>

""")
    link_verification = link
    print(email)
    message = t.substitute({"link": f"{link_verification}"})
    msg = EmailMultiAlternatives(
        'Subject',
        f"Reset your password with this link {link_verification}",
        settings.EMAIL_HOST_USER,
        [email],
    )
    msg.attach_alternative(message, "text/html")
    # Main content is now text/html
    msg.send()
    messages.info(request, "Mail successfully sent")


"""
def download_html(request, pk=None):
    user = request.user
    file_path = f"{settings.BASE_DIR}" + r"\records" + f"\{user.unique}.csv"
    p = pd.read_csv(file_path)
    v = len(p.values)
    p = p.iloc[int(pk)]
    doc = notes(request, pk).getvalue()
    with open(p.files + r"\record.html", "w") as f:
        f.write(r"{}".format(doc))
    with open(p.files + r"\record.txt", "w") as f:
        f.write(r"{}".format(request.POST["transcribes"]))
    return JsonResponse({"status": 400})


results_dict = {}


def mainner(text, path, unit, topic):
    p = word_return(text)
    t = ceil((len(p) * 0.03) // 100)
    if t == 0: t = 3
    t = t + 1

    queries = p[:t]
    print(queries)
    results_dict[topic + " " + unit] = se_arch(topic + " " + unit)
    for q in queries:
        print(q[0])
        results = se_arch(q[0] + " " + topic + " " + unit)
        results_dict[q[0] + " " + topic + " " + unit] = results
    with open(path + r"\results.json", "w") as f:
        json.dump(results_dict, f)


def note_data(request, pk=None):
    user = request.user
    file_path = f"{settings.BASE_DIR}" + r"\records" + f"\{user.unique}.csv"
    p = pd.read_csv(file_path)
    v = len(p.values)
    p = p.iloc[pk]

    with open(p.files + r"\record.txt", "r") as f:
        notes = f.read()
        notes = nltk.word_tokenize(notes)
    with open(p.files + r"\results.json") as f:
        j = json.load(f)
        imgs = []
        google = []
        youtube = []
        classmates = []
        for i in j.keys():
            imgs.extend([j[i]["images"][val] for val in j[i]["images"].keys()])
            _ = [google.append([j[i]["google"][val], val]) for val in j[i]["google"].keys()]

            youtube.extend([val.split("?v=")[1] for val in j[i]["youtube"]])
        for _ in (notes):
            classmates.append([[f"love{y}", y] for y in range(4)])
        print(classmates)
        counter = [i for i in range(len(notes) + 1)]
    return JsonResponse({"notes": notes, "counter": counter, "other_pics": imgs,
                         "articles": google, "classmates": classmates, "videos": youtube})
"""
