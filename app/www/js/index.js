var app = {
    preferences: {
        api_url: 'http://192.168.0.12:8000',
        threshold: 0.15,
        history: []
    },
    tabs_list: ['history', 'gallery', 'results'],
    tabs : {
        history: document.getElementById('tabs').getElementsByTagName("div")[0],
        gallery: document.getElementById('tabs').getElementsByTagName("div")[1],
        results: document.getElementById('tabs').getElementsByTagName("div")[2]
    },
    // Application Constructor
    initialize: function () {
        document.addEventListener('deviceready', this.init.bind(this), false);
    },


    init: function () {

        //Permissions:
        var permissions = cordova.plugins.permissions;
        permissions.hasPermission(permissions.READ_EXTERNAL_STORAGE, function( status ){
            if ( !status.hasPermission ) {
                permissions.requestPermission(permissions.READ_EXTERNAL_STORAGE, function(status){if( !status.hasPermission ) navigator.app.exitApp(); }, function(){navigator.app.exitApp();});
            }
          });

        this.setupCameraPreview();
        this.initCallback();
        

        if (this.isPreferencesSet()) {
            console.log("Loading preferences...");
            this.loadPreferences();
        } else {
            console.log("Init preferences");
            this.savePreferences();
        }
        this.setupParameters();
        this.setupGallery();
        this.setupHistory();
    },
    initCallback: function () {
        document.getElementById('bTakePicture').onclick = this.takePicture;
        document.getElementById('bFromGallery').onclick = this.galleryChooseImage;


        var front = document.getElementById('front-panel');
        var front_header = document.getElementById('front-panel-header').childNodes[0];
        var background = document.getElementById('background');
        hammer = new Hammer(front);
        hammer.get('swipe').set({
            direction: Hammer.DIRECTION_ALL
        });
        hammer.on('swipeup', function (event) {
            app.openPanel();
        });
        hammer.on('swipedown', function (event) {
            app.closePanel();
        });

        //Setup tabs
        for(var i = 0; i < this.tabs_list.length; i++){
            this.tabs[this.tabs_list[i]].onclick= this.changeActiveTabEvent.bind(app);
        }
    },
    setupCameraPreview: function () {
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
    takePicture: function () {
        console.log("Taking a picture !");
        CameraPreview.takePicture({
            width: 640,
            height: 640,
            quality: 85
        }, app.sendPicture.bind(app));
    },
    sendPicture: function (image) {
        this.toggleLoader();

        var url = this.preferences.api_url + '/img_searches';
        /* base64: base64 de l'image au format png ou jpg */

        //si ne commence pas par data: alors on ajoute data:image/jpeg;base64,
        if (!image.includes('data:image/')) {
            image = 'data:image/jpeg;base64,' + image;
        }

        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);

        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 201) {
                console.log("image sent ! Go to " + this.responseText);
                app.toggleLoader();
                
                var url = JSON.parse(this.responseText)['Location'];
                app.insertHistory(url);

                app.fetchResult(url);
            } else if (this.readyState === XMLHttpRequest.DONE) {
                console.error("Can't send the image! " + this.status + ':' + this.responseText);
                window.plugins.toast.showLongCenter("Impossible de contacter le serveur");
                app.toggleLoader();

            }
        };
        xhr.send(JSON.stringify({
            'base64': image
        }));
    },
    fetchResult: function(url){
        url = this.preferences.api_url + url;

        
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        document.getElementById('results-template').innerHTML = '<div style="padding-top:5em;"><div class="small-loader"></div></div>';
        this.tabs.results.classList.remove("inactive");
        this.changeActiveTab(this.tabs.results);
        this.openPanel();

        xhr.onload = onreadystatechange = function () {
            var template = document.getElementById('results-template');
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                var response = JSON.parse(this.responseText);
                var date = response.date;
                
                template.innerHTML = '<div class="response"><div class="date">Recherche du ' + date.slice(0, date.length-10) + '</div>';
                for(result of response.results){
                    if(result.score > app.preferences.threshold){
                        template.innerHTML += '<div class="result"><img src="' + app.preferences.api_url + '/static' + result.image_url + '" /><p class="brand">' + result.marque + '</p><div class="score">' + result.score + '</div></div>'; 
                    }
                }
                
            } else if (this.readyState === XMLHttpRequest.DONE) {
                console.error("Can't get the search results!");
                template.innerHTML = '<div class="error">Impossible de récupérer les résultats de votre recherche</div>';
            }
            app.reloadTabContent();
        };
        xhr.send();
    },
    isPreferencesSet: function () {
        return (localStorage.length == 3);
    },
    loadPreferences: function () {
        this.preferences.api_url = localStorage.getItem('api_url');
        this.preferences.history = JSON.parse(localStorage.getItem('history'));
        this.preferences.threshold = localStorage.getItem('threshold');
    },
    savePreferences: function () {
        localStorage.setItem('api_url', this.preferences.api_url);
        localStorage.setItem('history', JSON.stringify(this.preferences.history));
        localStorage.setItem('threshold', this.preferences.threshold);
    },
    toggleLoader: function () {
        for (var element of document.getElementsByClassName('loader')) {
            element.classList.toggle('hidden');
        }
    },
    setupGallery: function(){
        galleryAPI.getMedias(function(images){
            var template = document.getElementById('gallery-template');
            template.innerHTML = '<div class="gallery">';
            for(var i = 0; i < images.length && i < 8; i++){
                var image = images[i];
                template.innerHTML += '<img src="data:image/png;base64,' + image.thumbnail +'" data-url="' + image.uri + '" onclick="app.galleryOpenImage(this)" />';
            }
            //TODO: choose image from native gallery
            template.innerHTML += '<div onclick="app.galleryChooseImage()"><i class="fas fa-images fa-10x"></div>';
            
            template.innerHTML += '</div>';
            app.reloadTabContent();
        }, function(){
            var template = document.getElementById('gallery-template');
            template.innerHTML = "<h3>Pas d'images disponibles.<h3>";

            app.reloadTabContent();
        });

    },
    galleryOpenImage: function(image){
        data = image.src;
        this.sendPicture(data);
        
    },
    galleryChooseImage: function(){
        navigator.camera.getPicture(app.sendPicture.bind(app), function(e){
            console.error(e);
            window.plugins.toast.showLongCenter("Impossible de récupérer cette image!");
        },{
            quality: 40,
            destinationType: Camera.DestinationType.DATA_URL,
            sourceType: Camera.PictureSourceType.PHOTOLIBRARY
        });
    },
    setupHistory: function(){
        var template = document.getElementById("history-template");
        if(this.preferences.history.length == 0){
            template.innerHTML = '<h3>Pas d\'historique.</h3>';
            return;
        }
        template.innerHTML = "<p>Historique des recherches: </p><br><ul>";
        for(req of this.preferences.history){
            template.innerHTML += '<li data-url="' + req.url + '" onclick="app.loadHistory(this)"><i class="fas fa-eye fa-2x"></i>  ' + req.date + '</li>';
        }
        template.innerHTML += "</ul>";
        app.reloadTabContent();
    },
    loadHistory: function(entry){
        this.fetchResult(entry.dataset.url);
    },
    setupParameters: function(){
        document.getElementById('params_url').value = this.preferences.api_url;
        document.getElementById('params_threshold').value = this.preferences.threshold;

    },
    insertHistory: function(req_url){
        this.preferences.history.push({
            date: new Date().toLocaleString(),
            url: req_url
        });
        this.savePreferences();
        this.setupHistory();
    },
    saveParameters: function(){
        this.preferences.api_url = document.getElementById('params_url').value;
        this.preferences.threshold = document.getElementById('params_threshold').value;
        this.savePreferences();
        window.plugins.toast.showShortCenter("Paramètres sauvegardés.");
        this.closeParameters()
    },
    openPanel: function() {
        document.getElementById('front-panel').classList.toggle('up', true);
        document.getElementById('background').classList.toggle('hidden', true);

        var front_header = document.getElementById('front-panel-header').childNodes[0];
        front_header.classList.remove('fa-angle-up');
        front_header.classList.add('fa-angle-down');
    },
    closePanel: function(){
        document.getElementById('front-panel').classList.toggle('up', false);

        var front_header = document.getElementById('front-panel-header').childNodes[0];
        front_header.classList.add('fa-angle-up');
        front_header.classList.remove('fa-angle-down');

        setTimeout(function () {
            document.getElementById('background').classList.toggle('hidden', false);
        }, 400);
    },
    openParameters: function(){
        document.getElementById('parameters').classList.remove('hidden');
    },
    closeParameters: function(){
        document.getElementById('parameters').classList.add('hidden');
    },    
    changeActiveTabEvent: function(event){
        var tab = event.srcElement;
        if(!tab.classList.contains('inactive')){
            for(var t of this.tabs_list){
                this.tabs[t].classList.remove('active');
            }
                
            tab.classList.add('active');
        }

        this.reloadTabContent();
    },
    changeActiveTab: function(tab){
        if(!tab.classList.contains('inactive')){
            for(var t of this.tabs_list){
                this.tabs[t].classList.remove('active');
            }
                
            tab.classList.add('active');
        }

        this.reloadTabContent();
    },
    reloadTabContent: function(){
        var tab_name = '';
        for(t of this.tabs_list){
            if(this.tabs[t].classList.contains('active')){
                tab_name = t;
                break;
            }
        }
        var template = document.getElementById(t + '-template');
        var content  = document.getElementById('tab-content');
        content.innerHTML = template.innerHTML;
    }
};

app.initialize();