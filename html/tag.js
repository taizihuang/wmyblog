const tagbase = supabase.createClient('https://cjloskjcogrkvhpkfooz.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c')

function enter(e, el){
    if (e.keyCode == 13) {
        update(el);
    }
}

function onerror(el, error){
    var user = $(el.closest('.LI')).find('.USER')[0]

    if (!error) {
        // $('<div>').appendTo('body').addClass('alert alert-success').html('操作成功').show().delay(1500).fadeOut();
        $("<div>").prependTo(user).addClass('alert alert-success').html('修改成功').show().delay(1500).fadeOut();
    }else{
        // $('<div>').appendTo('body').addClass('alert alert-success').html('操作失败，请重试').show().delay(1500).fadeOut();
        $("<div>").prependTo(user).addClass('alert alert-success').html('修改失败，请重试').show().delay(1500).fadeOut();
    }
}

async function update(el){
    tag = el.val();
    md5 = el.data('md5');
    date_str = new Date().toISOString().slice(0, 19).replace('T', ' ');

    if (tag != ''){
    $.find(`[data-md5='${md5}']`)[0].value = tag;
    const {count, error} = await tagbase.from('tag').select('*', {count:'exact',head: true }).eq('id',md5);
    if (count == 0) {
        const {error} = await tagbase.from('tag').insert({id: md5, tag: tag});
        onerror(el, error);
    } else{
        const { error } = await tagbase.from('tag').update({'tag': tag,'created_at': date_str}).eq('id', md5);
        onerror(el, error);
    };
    }
}