import requests
from flask import Flask,request,abort,render_template,redirect
from linebot import(LineBotApi,WebhookHandler)
from linebot.exceptions import(InvalidSignatureError)
from linebot.models import(MessageEvent,TextMessage,TextSendMessage)
import mysql.connector
app=Flask(
    __name__,
    static_folder="static", #靜態檔案的資料夾名稱
    static_url_path="/"    #靜態檔案對應的網址路徑
    )
app.secret_key="123"
con=mysql.connector.connect(
    user='root',
    password='test',
    host='127.0.0.1',
    database='mydb',
    port=3306
)
# Channel access token 
linebotapi=LineBotApi('WUaSESn5nXHHQRdrSrWf1Sn5em2gWKiH6N6NIjRk1PoQ/Ap9EUameTPFJWbz5I9GAvcc0jki+OPi9YZ8YQynjpFukn16ExHCeKxFg7I2tEPOu+qEpLyB8/vUHtrIKLB+DtIECHzW/wFfA1+Q3rdI2AdB04t89/1O/w1cDnyilFU=')
# Channel secret
handler=WebhookHandler('792e0f8b1b4da62f9db97320e34c1829')
#USER ID
user_id='U6b846a05ecc5fe9d4909e6fe0eeddfbd'
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/signin",methods=["POST"])
def signin():
    password=request.form["password"]
    email=request.form["email"]
    cursor=con.cursor()
    cursor.execute("select * from account where email=%s",(email,))
    data=cursor.fetchall()
    if data[0][1]==password:
        return "welcome"
    return redirect("/error?msg=密碼輸入錯誤")
@app.route("/signup",methods=["POST"])
def signup():
    name=request.form["name"]
    password=request.form["password"]
    email=request.form["email"]
    if name==''or password==''or email=='':
        return redirect("/error?msg=留有空格請重新輸入")
    cursor=con.cursor()
    cursor.execute("select * from account where email=%s",(email,))
    data=cursor.fetchall()
    if len(data)!=0:
        return redirect("/error?msg=信箱已經被註冊")
    cursor.execute("insert into account(name,password,email) values (%s,%s,%s)",(name,password,email))  
    con.commit()
    linebotapi.push_message(user_id,TextSendMessage(text='新會員:'+name+' 成功加入'))
    return redirect("/?註冊成功")
#Line部分
# Channel access token 
linebotapi=LineBotApi('WUaSESn5nXHHQRdrSrWf1Sn5em2gWKiH6N6NIjRk1PoQ/Ap9EUameTPFJWbz5I9GAvcc0jki+OPi9YZ8YQynjpFukn16ExHCeKxFg7I2tEPOu+qEpLyB8/vUHtrIKLB+DtIECHzW/wFfA1+Q3rdI2AdB04t89/1O/w1cDnyilFU=')
# Channel secret
handler=WebhookHandler('792e0f8b1b4da62f9db97320e34c1829')       
## 接收賴訊息的地方
@app.route('/callback',methods=['POST'])
def callback():
    signature=request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    app.logger.info('Request body:'+body)
    try:
        #print(body,signature)
        handler.handle(body,signature)
        #print('---------------------------')
        #print(body)
    except InvalidSignatureError:#跳錯
        abort(400)
    return 'ok'
@app.route("/error")    
def error():
    message=request.args.get("msg","發生錯誤,請聯繫客服")
    return render_template("error.html",message=message)
##回復賴訊息的地方
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    linebotapi.reply_message(event.reply_token,TextSendMessage(text='hihi'))
    print(event.message.text)#在line上發出的訊息    
app.run(debug=True)