# farmero_nodejs_pca

sudo docker pull akumarmandapati3067/farmero_final:latest
sudo docker images
sudo docker run --name farmero_server -p 3000:3000 -d 9623029527c9

exec into the container - authenicate via the earthengine api

sudo docker exec -it farmero_server bash

earthengine authenticate --quiet

Open the URL which is shown and follow until you get the code
And inside the code in the following command

earthengine authenticate --authorization-code=PLACE_AUTH_CODE_HERE
login to earthengine and agree to access.

place the URL : 
http://0.0.0.0:3000/?coord=[[12.941725850371768,51.57971352400993],[12.942047715453555,51.57588640768779],[12.940846085814883,51.571032040481654],[12.943442464141299,51.57112539858611],[12.944708466796328,51.570671943139885],[12.948763966826846,51.57088533450155],[12.949965596465518,51.57121875649885],[12.951789498595645,51.570325180040776],[12.954450249938418,51.57021848317042],[12.954471707610537,51.571432145293755],[12.946274876861025,51.580113552408065],[12.941725850371768,51.57971352400993]]

