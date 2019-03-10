var bindFilters = function(){
    var sectionWidthSelector = document.getElementById('section_width'),
        profileSelector = document.getElementById('profile'),
        wheelDiameterSelector = document.getElementById('wheel_diameter'),
        allSelectors = document.querySelectorAll('select'),

        applyFilters = function(){
            var queries = [],
                stringQueries

            allSelectors.forEach(function(s){
                var attr = s.id,
                    value = s.value,
                    query

                if (value){
                    query = `${attr}=${value}`
                    queries.push(query)
                }
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

bindFilters()
