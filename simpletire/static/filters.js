var bindFilters = function(){
    'use strict'
    var sectionWidthSelector = document.getElementById('section_width'),
        aspect_ratioSelector = document.getElementById('aspect_ratio'),
        wheelDiameterSelector = document.getElementById('wheel_diameter'),
        allSelectors = document.querySelectorAll('select'),

        applyFilters = function(){
            var queries = [],
                stringQueries,
                elementsToHide = document.querySelectorAll('.hide-on-filter-change')

            allSelectors.forEach(function(s){
                var attr = s.id,
                    value = s.value,
                    query

                if (value){
                    query = `${attr}=${value}`
                    queries.push(query)
                }
            })

            elementsToHide.forEach(function(el){
                makeTransparent(el)
            })

            if (queries.length > 0){
                stringQueries = queries.join('&')
                window.location = `/?${stringQueries}`
            }else{
                window.location = '/'
            }


        }

    allSelectors.forEach(function(s){
        s.addEventListener('input', applyFilters)
    })

}

var showAdditionalFilters = function(){
    'use strict'
    var el = document.getElementById('additional-filters')

    makeOpaque(el)

}

var makeOpaque = function(el){
    'use strict'
    if(el){
        el.classList.add('opaque')
        el.classList.remove('transparent')
    }
}

var makeTransparent = function(el){
    'use strict'
    if(el){
        el.classList.remove('opaque')
        el.classList.add('transparent')
    }
}


var displayBlock = function(el){
    'use strict'
    if(el){
        el.style.display = 'table-cell'
    }
}

var displayNone = function(el){
    'use strict'
    if(el){
        el.style.display = 'none'
    }
}



// TODO DRY up bindStddevOptions and bindUtqgOptions
// as they are almost identical
var bindStddevOptions = function(){
    'use strict'
    var box = document.getElementById('show-stddev')

    box.addEventListener('change', function(e){
        var elements = document.querySelectorAll('.stddev')

        if (e.target.checked){
            elements.forEach(function(el){
                displayBlock(el)
            })
        }else{
            elements.forEach(function(el){
                displayNone(el)
            })
        }
    })


}

var bindUtqgOptions = function(){
    'use strict'
    var box = document.getElementById('show-utqg')

    box.addEventListener('change', function(e){
        var elements = document.querySelectorAll('.utqg')

        if (e.target.checked){
            elements.forEach(function(el){
                displayBlock(el)
            })
        }else{
            elements.forEach(function(el){
                displayNone(el)
            })
        }
    })


}


var bindTitle = function(){
    'use strict'
    var title = document.getElementById('page-title')

    title.addEventListener('click', function(){
        window.location = '/'
    })
}


bindFilters()
bindStddevOptions()
bindUtqgOptions()
bindTitle()
setTimeout(showAdditionalFilters, 4000)
