% rebase('base.tpl', title='EU data reporter - Random', **locals())
<div class="section">
  <div class="container">
    <br>
    <br>
    <h4 class="header blue-text">{{header}}</h1>
    <div class="row flow-text">

      {{!body}}

      <style>
      .highcharts-container, svg:not(:root) {
          overflow: visible !important;
      }
      </style>
    </div>
  </div>
</div>
