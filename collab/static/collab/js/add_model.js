$(document).ready(function(){

    $('.ui.selection.dropdown')
      .dropdown()
    ;

    var counter = 1;
    var limit = 20;
    function addInput(divName){
         if (counter == limit)  {
              alert("You have reached the limit of adding " + counter + " inputs");
         }
         else {
              var newdiv = document.createElement('div');
              newdiv.innerHTML = `
              <br><div class="ui input">
                 <input type="text" placeholder="Nom du champ" name='field_name'>
               </div>
              <div class="ui selection dropdown">
              <input type="hidden" name="field_type">
              <i class="dropdown icon"></i>
              <div class="default text">Type`
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
              $('.ui.selection.dropdown')
                .dropdown()
              ;

         }
    }

    // form validation
    $('.addfeaturemodel')
      .form({
        fields: {
          project:  {
            identifier: 'project',
            rules: [
              {
                type   : 'empty',
                prompt : 'Veuillez choisir un projet'
              }
            ]
          },
          feature:  {
            identifier: 'feature',
            rules: [
              {
                type   : 'empty',
                prompt : 'Veuillez entrer un nom pour ce type de signalement'
              }
            ]
          },
          geometry:  {
            identifier: 'geometry',
            rules: [
              {
                type   : 'empty',
                prompt : 'Veuillez choisir un type de géometrie pour ce signalement'
              }
            ]
          },
        }
      })
    ;
})
