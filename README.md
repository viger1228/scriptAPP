# ScriptAPP
**ScriptAPP** is the easy way to manage python script as task
## Installing
First, you should install python3 and pip3 in your computer.

Clone from the github

    >> git clone git@github.com:viger1228/scriptAPP.git
Install requirement package

    >> cd scriptAPP
    >> pip3 install -r requirement.txt

## Testing
There are two way to test your script.

Execute the script directly

    >> app/script/demo.py --help
    usage: demo.py [-h] [--message] function

    positional arguments:
      function    {demo}

    optional arguments:
      -h, --help  show this help message and exit
      --message   send the message

    >>  app/script/demo.py demo --message HelloWorld
    [2018-06-24 23:47:27,017][INFO][demo.py(line:38)] - HelloWorld
    [2018-06-24 23:47:27,018][INFO][tool.py(line:101)] - 0.0001 sec

Setting the schedule.yml  and execute run.py

    >> cat app/schedule.yml
    script:
    - name: demo
      setting:
        args: []
        kwargs: {'function':'demo','message':'Interval is running'}
        trigger: 'interval'
        hours: 0
        minutes: 0
        seconds: 5
    - name: demo
      setting:
        args: []
        kwargs: {'function':'demo','message':'Cron is running'}
        trigger: 'cron'
        hour: '*'
        minute: '*'
        second: '*/5'

    >> ./run.py 
    [2018-06-24 23:51:02] -  Start Job App
    [2018-06-24 23:51:05,002][INFO][demo.py(line:38)] - Cron is running
    [2018-06-24 23:51:05,002][INFO][tool.py(line:101)] - 0.0003 sec
    [2018-06-24 23:51:07,580][INFO][demo.py(line:38)] - Interval is running
    [2018-06-24 23:51:07,580][INFO][tool.py(line:101)] - 0.0002 sec

## Deployment
Running the program with the nohup 

Install the nohup 

    >> yum install nohup -y

Running

    >> ./nohup.sh start
    [2018-06-24 23:54:07] -  Start Job App
    walker   53991 37.0  1.1 224212 21424 pts/2    S+   23:54   0:00 python3 -u run.py scriptAPP

    >> tailf logs/20180624.log 
    [2018-06-24 23:54:45,004][INFO][demo.py(line:38)] - Cron is running
    [2018-06-24 23:54:45,005][INFO][tool.py(line:101)] - 0.0004 sec
    [2018-06-24 23:54:47,747][INFO][demo.py(line:38)] - Interval is running
    [2018-06-24 23:54:47,747][INFO][tool.py(line:101)] - 0.0003 sec
