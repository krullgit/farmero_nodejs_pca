const express = require('express')
const app = express()
const port = 3000



app.get('/', function(req, res) {

    const spawn = require('child_process').spawn;
    const ls = spawn('python', ['test.py', '[[13.272943496704102, 52.26377127581493],[13.275260925292969, 52.25586469803543],[13.288092613220215, 52.2596999583217],[13.292684555053711, 52.26650278898101],[13.296761512756348,52.27017956020817],[13.296289443969727,52.27123001026625],[13.288435935974121,52.26933918223966],[13.28174114227295,52.26834121271067],[13.272943496704102,52.26377127581493]]', 'arg2']);
    var back = ''

    ls.stdout.on('data', (data) => {
        back = data 
        console.log(back.toString())
        res.download('out2.jpg')
        //setTimeout(function(){res.download('out2.jpg')}, 1);
    });
    ls.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });
    ls.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))

