import * as am5 from '@amcharts/amcharts5'
import * as am5map from '@amcharts/amcharts5/map'
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated'

export default defineNuxtPlugin(() => {
  return {
    provide: {
      am5: {
        core: am5,
        map: am5map,
        themes: {
          Animated: am5themes_Animated,
        },
      },
    },
  }
})
