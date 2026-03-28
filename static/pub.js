function bindUpload(){
    $("#image-upload").on("change",function(event){
        let file = event.target.files[0];
        if(!file) return;

        const formData = new FormData();
        formData.append('picture' , file);

        $.post({
            url:'/upload/picture',
            data:formData,
            processData: false,
            contentType: false,
            success:function(result){
                let category = result['category'];
                let filename = result['filename'];
                console.log(category);
                console.log(filename);

                let imgPreview = $('#image-preview');
                imgPreview.attr('src' ,'/media/' + filename )
                imgPreview.removeClass('hidden');

                $('#image-placeholder').addClass('hidden');

                $('#category').val(category.id);

                $('#picture').val('/media/'+filename);
            }
        })
    })
}

$(function (){
    bindUpload();
})