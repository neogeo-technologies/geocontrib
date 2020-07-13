Vue.component('basemap-form-item', {
  delimiters: ['[[', ']]'],
    props: ['basemap', 'indexBaseMap'],
    template: `
    <div class="basemap">
      <h2>Fond de carte</h2>
      <div class="field">
        <label class="label" for="basemap-title">Titre</label>
        <input id=basemap-title type="text" v-model="basemap.title" class="input">
      </div>

      <div>
        <h4>Couches</h4>
        <div v-for="(layer, indexLayer) in basemap.layers" class="layer">
          <div class="field">
            <label class="label" for="layer-title">Titre</label>
            <input id=layer-title type="text" v-model="layer.title" class="input">
            <i class="close icon" @click="$emit('delete-from-list', indexBaseMap, indexLayer)"></i>
          </div>
          <div class="field">
            <label for="layer-opacity">Opacité</label>
            <div class="range-container">
              <input type="range" name="layer-opacity" min="0" max="1" step="0.01" v-model="layer.opacity">
              <output class="bubble">[[ getOpacityInPercentage(layer.opacity)]]</output>
            </div>
          </div>
          <div class="field">
            <label for="layer-order">Ordre</label>
            <input class="input" type="number" name="layer-order" id="layer-order" v-model="layer.order">
          </div>
        </div>
      </div>
    </div>
    `,
    methods: {
      getOpacityInPercentage: function (opacity) {
        return Math.round(opacity * 100);
      },
    }
});