const express = require('express')
const app = express()
const port = 3000


// var child_process = require('child_process');

// child_process.exec('python test4.py', function (err){
//     if (err) {
//         console.log("child processes failed with error code: " + err.code);
//     }
// });

// var back = ''



app.get('/', function(req, res) {

   
    //  START ---- get two NVDI images from Earth Engine and save them ---- START

    const coord = '[[12.941725850371768,51.57971352400993],[12.942047715453555,51.57588640768779],[12.940846085814883,51.571032040481654],[12.943442464141299,51.57112539858611],[12.944708466796328,51.570671943139885],[12.948763966826846,51.57088533450155],[12.949965596465518,51.57121875649885],[12.951789498595645,51.570325180040776],[12.954450249938418,51.57021848317042],[12.954471707610537,51.571432145293755],[12.946274876861025,51.580113552408065],[12.941725850371768,51.57971352400993]]'

    const spawn1 = require('child_process').spawn;
    //const ls1 = spawn1('/home/matthes/anaconda2/envs/googleapi/bin/python', ['test.py', '[[13.272943496704102, 52.26377127581493],[13.275260925292969, 52.25586469803543],[13.288092613220215, 52.2596999583217],[13.292684555053711, 52.26650278898101],[13.296761512756348,52.27017956020817],[13.296289443969727,52.27123001026625],[13.288435935974121,52.26933918223966],[13.28174114227295,52.26834121271067],[13.272943496704102,52.26377127581493]]', 'arg2']);
    const ls1 = spawn1('/home/matthes/anaconda2/envs/googleapi/bin/python', ['test.py', coord, 'arg2']);
    
    var back = ''

    ls1.stdout.on('data', (data) => {
        back = data 
        console.log(back.toString())
        



         // START ---- open the NVDI Images, process the PCA on it and save it to a file called "changemap.jpg" ---- START

        const spawn2 = require('child_process').spawn;
        const ls2 = spawn2('/home/matthes/anaconda2/bin/python', ['test4.py']);
        
        var back = ''

        ls2.stdout.on('data', (data) => {
            back = data 
            console.log(back.toString())
            



            // START ---- calculate change points ---- START 

            const spawn3 = require('child_process').spawn;
            //const ls1 = spawn1('/home/matthes/anaconda2/envs/googleapi/bin/python', ['test.py', '[[13.272943496704102, 52.26377127581493],[13.275260925292969, 52.25586469803543],[13.288092613220215, 52.2596999583217],[13.292684555053711, 52.26650278898101],[13.296761512756348,52.27017956020817],[13.296289443969727,52.27123001026625],[13.288435935974121,52.26933918223966],[13.28174114227295,52.26834121271067],[13.272943496704102,52.26377127581493]]', 'arg2']);
            const ls3 = spawn3('/home/matthes/anaconda2/envs/googleapi/bin/python', ['test5.py', coord, 'arg2']);
            
            var back = ''

            ls3.stdout.on('data', (data) => {
                back = data 
                console.log(back.toString())
                res.download('data/points.txt')
                //res.download('out2.jpg')
                //setTimeout(function(){res.download('out2.jpg')}, 1);
            });
            ls3.stderr.on('data', (data) => {
                console.log(`stderr: ${data}`);
            });
            ls3.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
            });

            // END ---- calculate change points ---- END 





        });
        ls2.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });
        ls2.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });


        // END ---- open the NVDI Images, process the PCA on it and save it to a file called "changemap.jpg" ---- END




    });
    ls1.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });
    ls1.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });


    //  END ---- get two NVDI images from Earth Engine and save them ---- END

    
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))

