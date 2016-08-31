/** функиция приводит к верхниму регистру каждое слово в элементе input[type='text'] */
function capitalize(rawInput) {
    var EXCLUSIONS = ['угли', 'углы', 'кызы', 'оглы', 'уулу'];
    var input = $(rawInput);

    input.focusout(function(){
        var text = input.val().trim();
        if ( !text ) return;    // опускаем обработку пустых строк

        // разобъем строку по пробельным символам и знакам тире
        var words = text.split(/(\s+|-)/);

        // обработаем каждое слово
        $(words).each(function(index, w){
            // преобразуем пробленые символ в единственны пробел и закончим обработку слова
            if (/\s/.test(w)) {
                words[index] = ' ';
                return;
            }

            // если это слово-исключения, пропустим его
            if ($.inArray(w, EXCLUSIONS) != -1)
                return;

            // первую букву к верхнему регистру
            var start = w.charAt(0).toUpperCase();

            // окончание, если есть, в нижний регистр
            var end = '';
            if (w.length > 1) {
                end = w.slice(1).toLowerCase();
            }

            // заменим страое слово
            words[index] = start + end;
        });
        // объедиминим массив слов в строку и поместим в качество нового значения поля
        input.val(words.join(''))

    })
}
