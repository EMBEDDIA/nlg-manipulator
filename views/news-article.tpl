% rebase('base.tpl', title='Vaalibotti Valtteri - Random', **locals())

<div class="section">
  <div class="container">
    <br>
    <br>
    <h1 class="header center blue-text">{{header}}</h1>
    <div class="row flow-text">
      <div class="card" style="float: right;">
        <div class="card-content">
          <span class="card-title">{{where}}</span>
          {{!locator_map}}
        </div>
      </div>

      {{!body}}

      <div class="card" style="float: left; clear: right;">
        <div class="card-content">
          {{!graph}}
        </div>
      </div>
    </div>
    <div class="row center">
      <a class="btn-large waves-effect waves-light-blue blue" href="/random">Uusi satunnainen uutinen</a>
    </div>
    <br>
    <br>
  </div>
</div>
