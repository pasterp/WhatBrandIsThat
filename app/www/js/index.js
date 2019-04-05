var app = {
    preferences: {
        api_url: 'http://192.168.0.12:8000'
    },
    // Application Constructor
    initialize: function() {
        document.addEventListener('deviceready', this.init.bind(this), false);
    },

 
    init: function() {
        this.receivedEvent('deviceready');
        this.setupCameraPreview();
        this.initCallback();

        if(this.isPreferencesSet()){
            console.log("Loading preferences...");
            this.loadPreferences();
        }else{
            console.log("Init preferences");
            this.savePreferences();
        }
        //console.log('Api url: ' + this.preferences.api_url);
    },
    initCallback: function(){
        document.getElementById('bTakePicture').onclick = this.takePicture;
    },

    // Update DOM on a Received Event
    receivedEvent: function(id) {
        console.log('Received Event: ' + id);
    },

    setupCameraPreview: function(){
        var options = {
            x: 0,
            y: 0,
            width: window.screen.width,
            height: window.screen.height,
            camera: CameraPreview.CAMERA_DIRECTION.BACK,
            toBack: true,
            tapPhoto: false,
            tapFocus: false,
            previewDrag: false,
            disableExifHeaderStripping: true
          };

          CameraPreview.startCamera(options);
    },
    /* -- Communication functions --*/
    takePicture: function(){
        console.log("Taking a picture !");
        CameraPreview.takePicture({width:640, height:640, quality: 85}, app.sendPicture.bind(app));
    },
    sendPicture: function(image){
        var url = this.preferences.api_url + '/img_searches';
        /* base64: base64 de l'image au format png ou jpg */

        //si ne commence pas par data: alors on ajoute data:image/jpeg;base64,
        if(!image.includes('data:image/')){
            image = 'data:image/jpeg;base64,' + image;
        }
        //console.log(image);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);

        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload =onreadystatechange = function() { 
            if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
                console.log("image sent ! Go to " + this.responseText);
                // that's good
            }else if(this.readyState === XMLHttpRequest.DONE){
                console.error("Can't send the image! " + this.status + ':' + this.responseText);
            }
        }
        xhr.send(JSON.stringify({'base64':image}));
    },
    isPreferencesSet: function(){
        return (localStorage.length > 0);
    },
    loadPreferences: function(){
        this.preferences.api_url = localStorage.getItem('api_url');
    },
    savePreferences: function(){
        localStorage.setItem('api_url', this.preferences.api_url);
    }
};

app.initialize();