<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>EU data reporter</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" type="text/css" href="/static/selectize.css" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.98.0/css/materialize.min.css">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">


    </head>
    <body>

      <nav class="blue" role="navigation">
        <div class="nav-wrapper container">
          <a id="logo-container" href="/" class="brand-logo">EU data reporter</a>
        </div>
      </nav>

      <main>
      {{!base}}
      </main>
      
      <form class="blue-text" action="/news?language=$language&where=$where">
        <div class="container">

          <label for="language"><b>Language</b></label>
          <input type="text" class="blue-text" name="language" required>

          <label for="where"><b>Country</b></label>
          <input type="text" class="blue-text" name="where" required>

          <label for="data"><b>Data</b></label>
          <input type="text" class="blue-text" name="data">

          <button type="submit" class="btn-large waves-effect waves-light-blue blue">Get report</button>
        </div>
      </form>

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
        });
      </script>
  </body>



</html>
