$('.ui.selection.dropdown')
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
             <input type="text" placeholder="Nom du champ" name='nom'>
           </div>
          <div class="ui selection dropdown">
          <input type="hidden" name="type">
          <i class="dropdown icon"></i>
          <div class="default text">Type` + (counter + 1)
           + `</div>
                <div class="menu">
                  <div class="item" data-value="int">int</div>
                  <div class="item" data-value="float">float</div>
                  <div class="item" data-value="date">date</div>
                  <div class="item" data-value="string">string</div>
                </div>
              </div>
          `;
          document.getElementById(divName).appendChild(newdiv);
          counter++;
     }
}
