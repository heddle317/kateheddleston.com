angularApp.controller('AdminTalksController', ['$scope', '$http', '$sce', function($scope, $http, $sce) {
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
                    'image_name': $scope.newImageName};
        $http.post("/admin/talks", data).success(function(data) {
            $scope.talks.unshift(data);
            $scope.newTitle = '';
            $scope.newDescription = '';
            $scope.newSlidesLink = '';
            $scope.newVideoLink = '';
            $scope.newImageName = '';
            $scope.newDate = '';
            $scope.newDescriptionLink = '';
            $scope.newLocation = '';
            $('#create_talk').modal('hide');
        });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
}]);

angularApp.controller('EditTalkController', ['$scope', '$http', '$log', function($scope, $http, $log) {
    $scope.editing = false;
    $scope.init = function(talk) {
        $scope.uuid = talk.uuid;
        $scope.title = talk.title;
        $scope.imageName = talk.image_name;
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
                    'image_name': $scope.imageName,
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
}]);

angularApp.controller('AdminGalleriesController', ['$scope', '$http', '$log', function($scope, $http, $log) {
    $scope.galleries = [];
    $scope.loading = true;
    $http.get('/admin/galleries').success(function(response) {
        $scope.galleries = response;
        var $container = $('#container');
        imagesLoaded($container, function() {
            $('.loading.main-loader').hide();
            $('#container').show();
            var msnry = new Masonry('#container', {columnWidth: 100,
                                                   itemSelector: ".item",
                                                   gutter: 10,
                                                   isFitWidth: true,
                                                   transitionDuration: 0});
        });
    });
}]);

angularApp.controller('MiniEditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.initGallery = function(gallery) {
        $scope.gallery = gallery;
        $scope.uuid = gallery.uuid;
        $scope.gallery_uuid = gallery.uuid;
        $scope.name = gallery.name;
        $scope.author = gallery.author;
        $scope.coverPhoto = gallery.cover_photo;
        $scope.items = gallery.items;
        $scope.published = gallery.published;
        $scope.published_ago = gallery.published_ago;
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
        $http.put("/admin/gallery/" + $scope.gallery_uuid, data).success(function(data) {
            $scope.editing = false;
        });
    };
}]);

angularApp.controller('EditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.gallery_uuid = galleryUUID;
    $scope.uuid = galleryUUID;
    $scope.name = '';
    $scope.author = '';
    $scope.coverPhoto = '';
    $scope.items = [];
    $scope.published = false;
    $scope.published_ago = '';
    $scope.editing = false;
    $scope.initGallery = function(gallery) {
        $scope.gallery = gallery;
        $scope.uuid = gallery.uuid;
        $scope.gallery_uuid = gallery.uuid;
        $scope.name = gallery.name;
        $scope.author = gallery.author;
        $scope.coverPhoto = gallery.cover_photo;
        $scope.items = gallery.items;
        $scope.published = gallery.published;
        $scope.published_ago = gallery.published_ago;
    };
    $http.get($window.location.pathname).success(function(response) {
        $scope.initGallery(response);
        if (!$scope.gallery_uuid) {
            $scope.editing = true;
        }
    });
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
          $window.location = "/blog/" + $scope.gallery_uuid;
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
      $http.delete("/admin/gallery/" + $scope.gallery_uuid).success(function(data) {
        for(var i=0; i < $scope.galleries.length; i++) {
          if($scope.galleries[i].uuid === $scope.gallery_uuid) {
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
      if ($scope.gallery_uuid) {
        var data = {'name': $scope.name,
                    'author': $scope.author,
                    'cover_photo': $scope.coverPhoto,
                    'items': $scope.items,
                    'published': $scope.published};
        $http.put("/admin/gallery/" + $scope.gallery_uuid, data).success(function(data) {
            $scope.editing = false;
        });
      } else {
        var data = {'name': $scope.name,
                    'author': $scope.author,
                    'cover_photo': $scope.coverPhoto,
                    'items': $scope.items};
        $http.post("/admin/galleries", data).success(function(response) {
            $scope.editing = false;
            $scope.initGallery(response);
            $window.location = "/admin/gallery/" + $scope.gallery_uuid;
        });
      }
    };
}]);

angularApp.controller('EditGalleryItemController', ['$scope', '$http', '$window', '$sce', '$upload', '$log', function($scope, $http, $window, $sce, $upload, $log) {
  $scope.file = [];
  $scope.dataUrls = [];
  $scope.item = null;
  $scope.error = false;
  $scope.alertMessage = '';
  $scope.loading = false;
  $scope.widthStyle = {"width": "0%"};
  $scope.generatingSizes = false;
  $scope.onFileSelect = function($files) {
    $scope.files = $files;
    for (var i = 0; i < $files.length; i++) {
      var file = $files[i];
      var timeStamp = new Date().getTime();
      var fileName = timeStamp + "_" + file.name;
      var fields = fileName.split('\.');
      fileName = fields[0];
      var key = "galleries/" + $scope.gallery_uuid + "/" + fileName;
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
        $scope.generatingSizes = true;
        $http.get('/blog/' + $scope.gallery_uuid + '/' + fileName + '/generate_sizes').success(function(data) {
            $scope.generatingSizes = false;
            $scope.item.image_name = fileName;
        });
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
}]);
