function bindUpload() {
    $("#image-upload").on("change", function (event) {
        let file = event.target.files[0];
        if (!file) return;

        const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
        const maxSize = 5 * 1024 * 1024;

        if (!allowedTypes.includes(file.type)) {
            alert("仅支持 JPG、PNG、WEBP 图片");
            $(this).val("");
            return;
        }

        if (file.size > maxSize) {
            alert("图片大小不能超过 5MB");
            $(this).val("");
            return;
        }

        const formData = new FormData();
        formData.append("picture", file);

        $.ajax({
            url: "/upload/picture",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (result) {
                if (!result.result) {
                    alert(result.message || "上传失败");
                    return;
                }

                let category = result.category;
                let pictureUrl = result.picture_url;

                let imgPreview = $("#image-preview");
                imgPreview.attr("src", pictureUrl);
                imgPreview.removeClass("hidden");

                $("#image-placeholder").addClass("hidden");
                $("#category").val(category.id);
                $("#picture").val(pictureUrl);
            },
            error: function (xhr) {
                let message = "上传失败，请稍后重试";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }
                alert(message);
            }
        });
    });
}

$(function () {
    bindUpload();
});