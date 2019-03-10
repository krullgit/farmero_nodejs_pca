# farmero_nodejs_pca


## Installation (depreciated) -> use docker_instructions instead

1. go to folder "python envs" and follow instructions in readme

2. go back to nodeServer folder and:

```bash
npm install
```
```bash
npm start
```

3. you probably need to open the server.js file and edit the following lines according to your conda paths of the environments you installed in the first step.
The paths to these envs can be obtained by:
```bash
source activate farmero_python2
```
```bash
which python 
```
```bash
source activate farmero_python3
```
```bash
which python 
```

Now, these paths has to be put as a replacement for:

/home/matthes/anaconda2/envs/farmero_python3/bin/python # (python 3 path)
/home/matthes/anaconda2/envs/farmero_python2/bin/python # (python 2 path)
/home/matthes/anaconda2/envs/farmero_python3/bin/python # (python 3 path)

4. open browser and with:
```bash
http://localhost:3000/?coord=[[12.941725850371768,51.57971352400993],[12.942047715453555,51.57588640768779],[12.940846085814883,51.571032040481654],[12.943442464141299,51.57112539858611],[12.944708466796328,51.570671943139885],[12.948763966826846,51.57088533450155],[12.949965596465518,51.57121875649885],[12.951789498595645,51.570325180040776],[12.954450249938418,51.57021848317042],[12.954471707610537,51.571432145293755],[12.946274876861025,51.580113552408065],[12.941725850371768,51.57971352400993]]
```

