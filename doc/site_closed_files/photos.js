var attributePhotos = function(){
    'use strict'
    var holderElements = document.querySelectorAll('.photo'),
        hyphenRegex = /-/g

    holderElements.forEach(function(el){
        var filename = el.getAttribute('name'),
            nameShort = filename.split('--')[1].split('.jpg')[0],
            nameWithSpaces = nameShort.replace(hyphenRegex, ' ')

        el.innerHTML = `<img src='/static/images/${filename}' class='img'></img><div class='photo__credit'>${nameWithSpaces}</div>`
    })

}

attributePhotos()
