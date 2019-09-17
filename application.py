from flask import Flask
from flask import request, session, render_template, json ,redirect,url_for
import datetime
import os

# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.secret_key = 'some random key'
dir_path = os.getcwd()

checkedBids ={}
bidsTime=[]
bidsSeconds=[]
global downloadFile
outputfile=[]
global VodUrl
global NoOfBids

@application.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
      return render_template('login.html')
    elif request.method =='POST':
      if request.form['username'] != "GAVL" or request.form['password'] != "3x}Sw7bBE{rkmgUZ":
        error = 'Invalid Credentials. Please try again.'
        return render_template('login.html', error=error)
      else:
        session['logged_in'] = True
        return redirect(url_for('auctionForm'))

@application.route('/logout', methods=['GET'])
def logout():
  session['logged_in'] = False
  return render_template('login.html')


@application.route('/auctionForm/', methods=['GET'])
def auctionForm():
         return render_template('auctionForm.html')

# it connects to the API and fetch the bids data
         # it calles getTime function to calcualte the time in seconds
         # it calles findVideoDuration to fetch the video length
         # it calles getIntroTime function to calculate the intro Time
         # it calles getOutroTime function to calaculate the outro time
@application.route('/fetchData/',methods=['POST'])
def fetchData():
    import requests
    auctionId =request.form["auctionId"]
    url = 'https://gavl-video-editing.gavl.com.au/v1/highlight-details'
    payload = '{"auctionId":\"'+str(auctionId)+'\","token":"a31e7e97737e3de8bd514c6eb888363e"}'
    headers = {
    'x-api-key': "0GkHKSNKJg25NKa3Zf3y02f8nFf6BmnQ623hn3zQ",
    'Content-Type': "application/json",
      }
    response = requests.request("POST", url, data=payload, headers=headers)
    auctiondata = json.loads(response.text)
    listBids=auctiondata['result']['bids']
    global VodUrl
    VodUrl= auctiondata['result']['vodURL']
    global NoOfBids
    NoOfBids=auctiondata['result']['noOfBids']
    streamAuctionTime = auctiondata['result']['streamStartTime']
    bidsTime,bidsSeconds=getTime(streamAuctionTime,auctiondata)
    duration=findVideoDuration(VodUrl)
    global introTime
    introTime=round(getIntroTime(0))
    global concluTime
    concluTime=getOutroTime(int(NoOfBids)-1,duration)

    return render_template('index.html', auction=auctionId,auctionUrl=VodUrl,
                           bids_input=zip(listBids,bidsTime,bidsSeconds),duration=duration,
                           introduction=introTime,confirmation=concluTime)


# to return the bids timestamp and also seconds
def getTime(streamAuctionTime,auctiondata):
    streamdatetime = datetime.datetime.strptime(streamAuctionTime, '%Y-%m-%dT%H:%M:%S.%fZ')
    for x in auctiondata['result']['bids']:
        y=x['bidTime']
        biddatetime = datetime.datetime.strptime(y, '%Y-%m-%dT%H:%M:%S.%fZ')
        bidsTime.append(biddatetime.time())
        bidsSeconds.append((abs(biddatetime-streamdatetime).seconds))
    return bidsTime,bidsSeconds

# it calcaulte the intro time in seconds
def getIntroTime(firstbid):
    firstbidTime=findTime(str(firstbid))
    introStartTime=int(firstbidTime)/2
    return introStartTime

# it calcaulte the outro time in seconds
def getOutroTime(lastbid,viedoLength):
    lastbidTime=findTime(str(lastbid))
    difference=float(viedoLength)-float(lastbidTime)
    difference=difference/2
    concluSartTime=round(lastbidTime+difference)
    return concluSartTime

# it process the form data by saving them in nested dictionary to be ready for generate function
    # it caclualtes the start and the end time from the pre/post buffers
    # it integrate the intro / outro parts if they are selected by calling
    # the method addIntroOutro
@application.route('/success/',methods=['POST'])
def success():
    # need validation if false ( not checked)all the checkbox >> empty dic >> back to auction form
    # x start from 0
    counter=0
    if(request.form.get("intro") and  ((int(request.form["preintro"])>0) or (int(request.form["postintro"])>0))):
        counter=addIntroOutro(checkedBids,"intro",introTime,counter)
    for x in range(NoOfBids):
        value = request.form.get(str(x))
        xbuffer=request.form["pre"+str(x)]
        ybuffer=request.form.get("post"+str(x))
        if (value and (int(xbuffer)!=0 or int(ybuffer)!=0)):        
           # prebuffer=request.form["pre"+str(x)]
            #postbuffer=request.form.get("post"+str(x))
            prebuffer=xbuffer
            postbuffer=ybuffer
            bid=request.form.get(str(x))
            time=findTime(str(x))
            starttime=time-int(prebuffer)
            endtime=time+int(postbuffer)          
            if(endtime-starttime == 1):
                #starttime=time-int(prebuffer)
                #endtime=time+int(postbuffer)
                if(starttime == time):
                 starttime=starttime-1
                if(endtime == time):
                 endtime=endtime+1
                checkedBids[counter] = {'bid':bid,'time':time,'prebuffer': prebuffer,
                             'postbuffer': postbuffer,'starttime':starttime,
                             'endtime':endtime}
                counter=counter+1
            else:
              #starttime=time-int(prebuffer)
              #endtime=time+int(postbuffer) 
              checkedBids[counter] = {'bid':bid,'time':time,'prebuffer': prebuffer,
                             'postbuffer': postbuffer,'starttime':starttime,
                             'endtime':endtime}
              counter=counter+1
        #counter=counter+1
    if(request.form.get("outro") and  ((int(request.form["preoutro"])>0) or (int(request.form["postoutro"])>0))):
        counter=addIntroOutro(checkedBids,"outro",concluTime,counter)
    if(checkedBids):
      outputfile=generate(checkedBids,len(checkedBids))
      return  render_template('download.html',videoid=str(outputfile))
    else:
        return redirect(url_for('auctionForm'))
        
    #return json.dumps(checkedBids)

# it add the intro/outro parts in the global dictionary (checkecBids) which is used to generate
  # the hilighted viedo
def addIntroOutro(checkedBids,boxid,time,index):
    prebuffer=request.form["pre"+str(boxid)]
    postbuffer=request.form.get("post"+str(boxid))
    bid=request.form.get(str(boxid))
    starttime=time-int(prebuffer)
    endtime=time+int(postbuffer)
    if(endtime-starttime == 1):
     if(starttime == time):
        starttime=starttime-1
     if(endtime == time):
        endtime=endtime+1
    checkedBids[index] = {'bid':bid,'time':time,'prebuffer': prebuffer,
                             'postbuffer': postbuffer,'starttime':starttime,
                             'endtime':endtime}
    counter=index+1
    return counter

#  find the time of a specific bid by searching the result of the getTime() method
def findTime(bidid):
    #checkedbidtime,checkedbidsecond=getTime()
    for t,s in zip(bidsTime,bidsSeconds):
        if(str(bidsSeconds.index(s))==bidid):
            return s

def trim(x,y,z):
    trimviedocommand="[0:v]trim=start="+str(x)+":end="+str(y-1)+",setpts=PTS-STARTPTS,format=pix_fmts=yuva420p,fade=t=in:st=0:d=1:alpha=1[videoPart"+str(z)+"];[0:a]atrim=start="+str(x)+":end="+str(y-1)+",asetpts=PTS-STARTPTS[audioPart"+str(z)+"]"
    last=trimviedocommand+";"
    return last

def fedoverly(x,y,z):
     fadecommand="[0:v]trim=start="+str(int(x)-1)+":end="+str(y)+",setpts=PTS-STARTPTS,format=pix_fmts=yuva420p,fade=t=out:st=0:d=1:alpha=1[videoPart"+str(z)+"Overlay];[0:a]atrim=start="+str(int(x)-1)+":end="+str(y)+",asetpts=PTS-STARTPTS[audioPart"+str(z)+"Fade];"
     return fadecommand


def contain(v1,v2,a1,a2,number):
    fadeoverlycontainer=v2+v1+'overlay[videoOverlay'+str(number)+'];'+a2+a1+'acrossfade=d=1[audioCrossfade'+str(number)+'];'
    return fadeoverlycontainer


# it creates the hilighted viedo by generating ffmpeg script by using the data
# from the dic (checkedBids)
def generate(checkedBids,length):
    videoname='videoPart'
    audioname='audioPart'
    import datetime
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    outputfilename = "_".join(["output", suffix,".mp4"])
    concatFiles=[]
    videoParts=[]
    audioParts=[]
    counter =1
    i=0
    arrayindex=0
    overlayname=1
    command=""
    start='ffmpeg -y -i '+str(VodUrl)+' -filter_complex \
     \"'
    #firstbid=min(checkedBids.keys(), key=(lambda k: checkedBids[k]))
    for bid in checkedBids:
            if(list(checkedBids.keys())[i]==list(checkedBids.keys())[0]):
               #print(examples[example])
               command=trim(checkedBids[i]['starttime'],checkedBids[i]['endtime'],counter)
               concatFiles.append('['+videoname+str(counter)+']')
               concatFiles.append('['+audioname+str(counter)+']')
               counter=counter+1
               i=i+1
            else:
               command=command+fedoverly(checkedBids[i-1]['endtime'],
                                         checkedBids[i-1]['endtime'],counter)
               videoParts.append("[videoPart"+str(counter)+"Overlay]")
               audioParts.append("[audioPart"+str(counter)+"Fade]")
               counter=counter+1
               command=command+trim(checkedBids[i]['starttime'],
                                    checkedBids[i]['endtime'],counter)
               videoParts.append("[videoPart"+str(counter)+"]")
               audioParts.append("[audioPart"+str(counter)+"]")

               command=command+contain(videoParts.pop(),videoParts.pop(),
                     audioParts.pop(),audioParts.pop(),overlayname)
               #command=command+contain(videoParts[arrayindex],videoParts[arrayindex+1],
                    #  audioParts[arrayindex],audioParts[arrayindex+1],overlayname)
               concatFiles.append('[videoOverlay'+str(overlayname)+']')
               concatFiles.append('[audioCrossfade'+str(overlayname)+']')
               counter=counter+1
               i=i+1
               arrayindex=arrayindex+1
               overlayname=overlayname+1

    concat=""

    for file in concatFiles:
       concat=concat+file

    dest_file = dir_path+'/static/video/' + outputfilename
    last=concat+"concat=n="+str(length)+":v=1:a=1[videoOut][audioOut]\" -map [videoOut] -map [audioOut] "+dest_file
    fullscript=start+command+last
    import subprocess
    subprocess.call(fullscript,shell=True)
    checkedBids.clear()
    concatFiles.clear()
    videoParts.clear()
    audioParts.clear()
    return dest_file

# function to find the duration of the input video file
def findVideoDuration(pathToInputVideo):
    import subprocess
    import shlex
    import json
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    # prints all the metadata available:
    #import pprint
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(ffprobeOutput)

    # for example, find height and width
   #height = ffprobeOutput['streams'][0]['height']
    duration = ffprobeOutput['streams'][0]['duration']

    #print(height, width)
    return duration

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
