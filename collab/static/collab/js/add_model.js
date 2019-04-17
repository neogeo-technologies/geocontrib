$('.ui.selection.dropdown.type')
  .dropdown()
;


var counter = 1;
var limit = 20;
function addInput(divName){

      $('.ui.selection.dropdown')
        .dropdown()
      ;
     if (counter == limit)  {
          alert("You have reached the limit of adding " + counter + " inputs");
     }
     else {

       $('.ui.selection.dropdown')
         .dropdown()
       ;

          var newdiv = document.createElement('div');
          newdiv.innerHTML = `
          <br><div class="ui input">
             <input type="text" placeholder="Nom du champ" name='field_name'>
           </div>
          <div class="ui selection dropdown">
          <input type="hidden" name="field_type">
          <i class="dropdown icon"></i>
          <div class="default text">Type` + (counter + 1)
           + `</div>
                <div class="menu">
                  <div class="item" data-value="int">Entier</div>
                  <div class="item" data-value="float">Flottant</div>
                  <div class="item" data-value="date">Date</div>
                  <div class="item"  data-value="string">ChaÎne de caractère</div>
                  <div class="item"  data-value="text">Text</div>
                  <div class="item"  data-value="boolean">Booléen</div>
                </div>
              </div>
          `;
          document.getElementById(divName).appendChild(newdiv);
          counter++;
     }
}
