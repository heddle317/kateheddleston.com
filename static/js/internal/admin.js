function TalksCtrl($scope, $http, $sce) {
    $scope.talks = [];
    $http.get('/admin/talks').success(function(data) {
        $scope.talks = data;
    });

    $scope.createTalk = function() {
        var data = {'title': $scope.newTitle,
                    'description': $scope.newDescription,
                    'slides_link': $scope.newSlidesLink,
                    'video_link': $scope.newVideoLink,
                    'description_link': $scope.newDescriptionLink,
                    'location': $scope.newLocation,
                    'date': $scope.newDate,
                    'image_link': $scope.newImageLink};
        $http.post("/admin/talks", data).success(function(data) {
            $scope.talks.unshift(data);
            $scope.newTitle = '';
            $scope.newDescription = '';
            $scope.newSlidesLink = '';
            $scope.newVideoLink = '';
            $scope.newImageLink = '';
            $scope.newDate = '';
            $scope.newDescriptionLink = '';
            $scope.newLocation = '';
            $('#create_talk').modal('hide');
        });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
};

function TalkCtrl($scope, $http) {
    $scope.editing = false;
    $scope.init = function(talk) {
        $scope.uuid = talk.uuid;
        $scope.title = talk.title;
        $scope.imageLink = talk.image_link;
        $scope.slidesLink = talk.slides_link;
        $scope.videoLink = talk.video_link;
        $scope.description = talk.description;
        $scope.descriptionLink = talk.description_link;
        $scope.location = talk.location;
        $scope.date = talk.date;
        $scope.published = talk.published;
    };
    $scope.cancel = function() {
        $scope.editing = false;
    };
    $scope.editTalk = function() {
        $scope.editing = true;
    };
    $scope.unpublishTalk = function() {
        $scope.published = false;
        $scope.updateTalk();
    };
    $scope.publishTalk = function() {
        $scope.published = true;
        $scope.updateTalk();
    };
    $scope.updateTalk = function() {
        var data = {'title': $scope.title,
                    'description': $scope.description,
                    'slides_link': $scope.slidesLink,
                    'video_link': $scope.videoLink,
                    'description_link': $scope.descriptionLink,
                    'location': $scope.location,
                    'date': $scope.date,
                    'image_link': $scope.imageLink,
                    'published': $scope.published};
        $http.put("/admin/talks/" + $scope.uuid, data).success(function(data) {
            $scope.editing = false;
        });
    };
    $scope.goToBlog = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/talk/" + $scope.uuid;
        }
    };
    $scope.deleteTalk = function() {
      var confirm = $window.confirm("Are you sure you want to delete this talk?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/talks/" + $scope.uuid).success(function(data) {
        for(var i=0; i < $scope.talks.length; i++) {
          if($scope.talks[i].uuid === $scope.uuid) {
            $scope.talks.splice(i, 1);
          }
        }
      });
    };
};

function GalleriesCtrl($scope, $http) {
    $scope.galleries = [];
    $scope.newName = '';
    $scope.newAuthor = '';
    $scope.newCoverPhoto = '';
    $scope.newItems = [];
    $http.get('/admin/galleries').success(function(response) {
        $scope.galleries = response;
    });
    $scope.addNew = function() {
      var position = $scope.newItems.length + 1;
      var item = {'title': '', 'body': '', 'image_name': '', 'position': position};
      $scope.newItems.push(item);
    };

    $scope.createGallery = function() {
        var data = {'name': $scope.newName,
                    'author': $scope.newAuthor,
                    'cover_photo': $scope.newCoverPhoto,
                    'items': $scope.newItems};
        $http.post("/admin/galleries", data).success(function(data) {
            $scope.galleries.unshift(data);
            $scope.newName = '';
            $scope.newAuthor = '';
            $scope.newItems = [];
            $('#create_gallery').modal('hide');
        });
    };
};

function GalleryCtrl($scope, $http, $window, $sce, $log) {
    $scope.init = function(gallery) {
      $scope.uuid = gallery.uuid;
      $scope.name = gallery.name;
      $scope.author = gallery.author;
      $scope.coverPhoto = gallery.cover_photo;
      $scope.items = gallery.items;
      $scope.published = gallery.published;
      $scope.published_ago = gallery.published_ago;
    };
    $scope.editing = false;
    $scope.editGallery = function() {
      $scope.editing = true;
    };
    $scope.addNewItem = function(position) {
      var item = {'title': '', 'body': '', 'image_name': '', 'position': position};
      $scope.items.splice(position - 1, 0, item);
      for (var i = position; i < $scope.items.length; i++) {
        $scope.items[i].position++;
      }
      $scope.editing = true;
    };
    $scope.removeItem = function(position) {
      $scope.items.splice(position - 1, 1);
      for (var i = position - 1; i < $scope.items.length; i++) {
        $scope.items[i].position--;
      }
      $scope.updateGallery();
    };
    $scope.goToGallery = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/blog/" + $scope.uuid;
        }
    };
    $scope.cancel = function() {
      $scope.editing = false;
    };
    $scope.deleteGallery = function() {
      var confirm = $window.confirm("Are you sure you want to delete this gallery?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/gallery/" + $scope.uuid).success(function(data) {
        for(var i=0; i < $scope.galleries.length; i++) {
          if($scope.galleries[i].uuid === $scope.uuid) {
            $scope.galleries.splice(i, 1);
          }
        }
      });
    };
    $scope.unpublishGallery = function() {
        $scope.published = false;
        $scope.updateGallery();
    };
    $scope.publishGallery = function() {
        $scope.published = true;
        $scope.updateGallery();
    };
    $scope.updateGallery = function() {
      var data = {'name': $scope.name,
                  'author': $scope.author,
                  'cover_photo': $scope.coverPhoto,
                  'items': $scope.items,
                  'published': $scope.published};
      $http.put("/admin/gallery/" + $scope.uuid, data).success(function(data) {
        $scope.editing = false;
      });
    };
};

function GalleryItemCtrl($scope, $http, $window, $sce, $upload, $log) {
  $scope.file = [];
  $scope.dataUrls = [];
  $scope.item = null;
  $scope.error = false;
  $scope.alertMessage = '';
  $scope.loading = false;
  $scope.widthStyle = {"width": "0%"};
  $scope.itemInit = function(item) {
    $scope.item = item;
  };
  $scope.onFileSelect = function($files) {
    $scope.files = $files;
    for (var i = 0; i < $files.length; i++) {
      var file = $files[i];
      var timeStamp = new Date().getTime();
      var fileName = timeStamp + "_" + file.name;
      var fields = fileName.split('\.');
      fileName = fields[0];
      var key = "galleries/" + galleryUUID + "/" + fileName;
      var data = {
            key: key,
            AWSAccessKeyId: accessKey, 
            acl: 'public-read',
            policy: policy,
            signature: signature,
            "Content-Type": file.type != '' ? file.type : 'application/octet-stream',
            filename: key,
      };
      $upload.upload({
        url: imagesBase,
        method: 'POST',
        data: data,
        file: file,
      }).progress(function(evt) {
        $scope.percent = parseInt(100.0 * evt.loaded / evt.total);
        $scope.widthStyle = {"width": $scope.percent + "%"};
        $scope.loading = true;
      }).success(function(data, status, headers, config) {
        $scope.item.image_name = fileName;
      }).error(function(data, status, headers, config) {
          $scope.error = true;
          $scope.alertMessage = "There was an error uploading your photo.";
      }).then(function() {
          $scope.loading = false;
      });
    }
  };
  $scope.toggleAlert = function(show) {
      $scope.error = show;
      $scope.alertMessage = '';
  };
};
