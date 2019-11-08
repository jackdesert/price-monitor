var bindFilters = function(){
    'use strict'
    var sectionWidthSelector = document.getElementById('section_width'),
        aspect_ratioSelector = document.getElementById('aspect_ratio'),
        wheelDiameterSelector = document.getElementById('wheel_diameter'),
        allSelectors = document.querySelectorAll('select'),
        nameSearch = document.getElementById('name'),
        nameSearchButton = document.getElementById('name-search-button'),

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

            if (nameSearch && nameSearch.value != ''){
                queries.push(`name=${nameSearch.value}`)
            }

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

    nameSearch.addEventListener('keyup', function(key){
        if (key.key === 'Enter'){
            applyFilters()
        }
    })

    nameSearchButton.addEventListener('click', applyFilters)


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

var bindOptionsCheckbox = function(className){
    'use strict'
    var box = document.getElementById('show-' + className)
    if (!box){ return }

    var triggerBox = function(){
        // Manually trigger changeEvent
        var changeEvent = document.createEvent('HTMLEvents')
        changeEvent.initEvent('change', true, false)
        box.dispatchEvent(changeEvent)
    }

    box.addEventListener('change', function(e){
        var elements = document.querySelectorAll('.' + className)
        console.log('responding to change', className)

        elements.forEach(function(el){
            if (e.target.checked){
                displayBlock(el)
            }else{
                displayNone(el)
            }
        })
    })

    return triggerBox
}


var bindTitle = function(){
    'use strict'
    var title = document.getElementById('page-title')

    title.addEventListener('click', function(){
        window.location = '/'
    })
}


function ready(fn) {
    // This function is a non-jquery version of document.ready.
    //
    if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading"){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}


var triggerStddev = bindOptionsCheckbox('stddev')
var triggerUtqg = bindOptionsCheckbox('utqg')
var triggerDiameter = bindOptionsCheckbox('diameter')

// Do these things when document is ready
// so that when you click the back button after visiting simpletire link
// then it will manually trigger the correct things
ready(triggerStddev)
ready(triggerUtqg)
ready(triggerDiameter)

bindFilters()
bindTitle()
setTimeout(showAdditionalFilters, 4000)





