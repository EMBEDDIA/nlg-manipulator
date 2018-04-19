<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>Vaalibotti Valtteri</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" type="text/css" href="/static/selectize.css" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.98.0/css/materialize.min.css">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

        <script>
          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

          ga('create', 'UA-93889406-1', 'auto');
          ga('send', 'pageview');

        </script>

        <style type="text/css">
          @media only screen and (min-width: 0) {
            html {
              font-size: 12px;
            }
          }

          @media only screen and (min-width: 992px) {
            html {
              font-size: 12px;
            }
          }

          @media only screen and (min-width: 1200px) {
            html {
              font-size: 12px;
            }
          }

          body {
            display: flex;
            min-height: 100vh;
            flex-direction: column;
          }

          main {
            flex: 1 0 auto;
          }

          #map-card {
            float: none;
            min-width: 350px;
          }

          #graph-card {
            float: none;
          }

          @media only screen and (min-width: 700px) {
            #map-card {
              float: right;
            }

            #graph-card {
              float: left;
              clear: right;
            }
          }
        </style>
    </head>
    <body>
    
      <nav class="light-blue lighten-1" role="navigation">
        <div class="nav-wrapper container">
          <a id="logo-container" href="/" class="brand-logo">Valtteri</a>
        </div>
      </nav>

      <main>
      <div class="section">
        <div id="search" class="container hide">
          <form action="news" method="post">
            <div class="row">
              <div class="col s12">
                <select id="location-search" name="location" placeholder="Sijainti"></select>
              </div>
            </div>
            <div class="row">
              <div class="col s12">
                <select id="language-select" name="language" placeholder="Language"></select>
              </div>
            </div>
            <div class="row">
              <div class="col s12">               
                <button class="right btn waves-effect waves-light-blue blue" type="submit" name="action">
                  Lue
                  <i class="material-icons right">send</i>
                </button>
              </div>
            </div>
          </form>
        </div>
        <div id="search-wait" class="container">
          <div class="row">
            <div class="col s12 valign-wrapper">
              <div class="preloader-wrapper big active" style="margin-left: auto; margin-right: auto;">
                <div class="spinner-layer spinner-blue-only">
                  <div class="circle-clipper left">
                    <div class="circle"></div>
                  </div><div class="gap-patch">
                    <div class="circle"></div>
                  </div><div class="circle-clipper right">
                    <div class="circle"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

     

      {{!base}}
      </main>
      <footer class="page-footer blue">
        <div class="container">
          <div class="row">
            <div class="col l6 s12">
              <h5 class="white-text">Vaalibotti Valtteri</h5>
              <p class="grey-text text-lighten-4">Vaalibotti Valtteri on tietokoneohjelma joka kirjoittaa vaaliuutisia vuoden 2017 kuntavaaleista Oikeusministeriön vaalitulosdatan pohjalta.</p>
              <p class="grey-text text-lighten-4">Valtterin taustalla on <a class="grey-text text-lighten-4" style="font-weight:bold" href="https://www.immersiveautomation.com">Immersive Automation</a> -konsortioprojekti.</p>
            </div>
            
            <div class="col l4 offset-l2 s12">
              <p class="grey-text text-lighten-4">
                <a class="grey-text text-lighten-4" style="font-weight:bold" href="tietosuoja">Tietosuojaseloste</a>
              </p>
            </div>
          </div>
        </div>
        <div class="footer-copyright">
            <div class="container"><p></p>
            </div>
          </div>
      </footer>


      <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.98.0/js/materialize.min.js"></script>
      <script type="text/javascript" src="/static/selectize.js"></script>
      <script type="text/javascript" src="/static/geolocate.js"></script>

      % setdefault('where', 'fi')
      % setdefault('where_type', 'C')
      % setdefault('language', 'FI')
      <script type="text/javascript">
        $(document).ready(function() {  

            function rec_add(geo_autocomplete, data, str) {
                str = str + " > " + data.name;
                geo_autocomplete.push({
                    text: str,
                    value: data.type + data.id,
                })
                for (var id in data.children) {
                    rec_add(geo_autocomplete, data.children[id], str);
                }
            }

            $.getJSON('api/languages', function(rawdata) {
                console.log(rawdata)
                languages = rawdata.languages;
                selectables = [];
                for (var i = 0; i < languages.length; i++) {
                    selectables.push({
                      text: languages[i],
                      value: languages[i]
                    });
                }
                languageSelectize = $('#language-select').selectize({
                    options: selectables,
                    items: ['{{language}}'],
                    closeAfterSelect: true,
                })[0].selectize;
            });
                
            var locationSelectize;
            $.getJSON('api/geodata?language={{language}}', function(rawdata) {
                data = rawdata.data;
                geo_autocomplete = [{text:data["fi"].name, value:"Cfi"}];
                for (var id in data["fi"].children) {
                    rec_add(geo_autocomplete, data["fi"].children[id], data["fi"].name);
                }
                locationSelectize = $('#location-search').selectize({
                    options: geo_autocomplete,
                    items: ['{{where_type}}{{where}}'],
                    closeAfterSelect: true,
                    onChange: function(value) {
                      updateEntitySelections(value);
                    }
                })[0].selectize;

                $('#search-wait').addClass('hide');
                $('#search').removeClass('hide');
            });
        });
      </script>
  </body>


        
</html>
