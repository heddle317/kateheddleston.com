angularApp.controller('AdminTalksController', ['$scope', '$http', '$sce', function($scope, $http, $sce) {
    $scope.talks = [];
    $scope.loading = true;
    $scope.published = false;
    $http.get('/admin/talks').success(function(response) {
        $scope.talks = response;
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
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
}]);

angularApp.controller('MiniEditTalkController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.initTalk = function(talk) {
        $scope.talk = talk;
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
        var data = {'published': $scope.published};
        $http.put("/admin/talks/" + $scope.talk.uuid, data).success(function(data) {
            $scope.editing = false;
            $scope.talk = data;
        });
    };
}]);

angularApp.controller('EditTalkController', ['$scope', '$http', '$log', '$window', '$sce', function($scope, $http, $log, $window, $sce) {
    $scope.editing = false;
    $scope.talk_uuid = talkUUID;
    $scope.talk = null;
    $scope.initTalk = function(talk) {
        $scope.talk = talk;
        $scope.talk_uuid = talk.uuid;
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
    $http.get($window.location.pathname).success(function(response) {
        $scope.initTalk(response);
        if (!$scope.talk_uuid) {
            $scope.editing = true;
        }
    });
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
                    'date': $scope.datee,
                    'image_name': $scope.talk.image_name};
        if ($scope.talk_uuid) {
            data['published'] = $scope.published;
            $http.put("/admin/talks/" + $scope.uuid, data).success(function(data) {
                $scope.editing = false;
            });
        } else {
            $http.post("/admin/talks", data).success(function(data) {
                $scope.editing = false;
                $scope.initTalk(data);
                $window.location = "/admin/talk/" + $scope.talk_uuid;
            });
        }
    };
    $scope.deleteTalk = function() {
      var confirm = $window.confirm("Are you sure you want to delete this talk?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/talks/" + $scope.uuid).success(function(data) {
          $window.location = "/admin/talks";
      });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
}]);

angularApp.controller('AdminGalleriesController', ['$scope', '$http', '$log', function($scope, $http, $log) {
    $scope.loading = true;
    $scope.items = {'published': [], 'unpublished': [], 'archived': [], 'permanent': []};
    $scope.currentContainer = '.published';
    $http.get('/admin/galleries').success(function(response) {
        $('.loading.main-loader').show();
        var i;
        var item;
        for (i = 0; i < response.length; i++) {
            item = response[i];
            if (item.published) {
                $scope.items['published'].push(item);
            } else if (item.archived) {
                $scope.items['archived'].push(item);
            } else if (item.permanent) {
                $scope.items['permanent'].push(item);
            } else {
                $scope.items['unpublished'].push(item);
            }
        };
        $scope.changeTab('unpublished');
    });
    $scope.sortLists = function() {
    };
    $scope.removeItem = function(uuid) {
        for (var listName in $scope.items) {
            if ($scope.items.hasOwnProperty(listName)) {
                var list = $scope.items[listName];
                for (var i = 0; i < list.length; i++) {
                    if (list[i].uuid == uuid) {
                        list.splice(i, 1);
                    }
                }
            }
        };
    };
    $scope.changeTab = function(className) {
        $('.loading.main-loader').show();
        $($scope.currentContainer).hide();
        $scope.currentContainer = '.' + className;
        $($scope.currentContainer).hide();
        imagesLoaded($($scope.currentContainer), function() {
            $($scope.currentContainer).show();
            $('.loading.main-loader').hide();
            var msnry = new Masonry($scope.currentContainer, {columnWidth: 100,
                                                              itemSelector: ".item",
                                                              gutter: 10,
                                                              isFitWidth: true,
                                                              transitionDuration: 0});
        });
    };
}]);

angularApp.controller('MiniEditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.initGallery = function(gallery) {
        $scope.gallery = gallery;
        $scope.gallery_uuid = gallery.uuid;
    };
    $scope.publishGallery = function(publish) {
        $scope.gallery.published = publish;
        $scope.gallery.archived = false;
        $scope.updateGallery();
    };
    $scope.archiveGallery = function(archive) {
        $scope.gallery.archived = archive;
        $scope.updateGallery();
    };
    $scope.updateGallery = function() {
        $scope.removeItem($scope.gallery.uuid);
        if ($scope.gallery.published) {
            $scope.items.published.push($scope.gallery);
        } else if ($scope.gallery.archived) {
            $scope.items.archived.push($scope.gallery);
        } else {
            $scope.items.unpublished.push($scope.gallery);
        }
        $scope.sortLists();
        var data = {'published': $scope.gallery.published,
                    'archived': $scope.gallery.archived};
        $http.put("/admin/gallery/" + $scope.gallery.uuid, data).success(function(data) {
        });
    };
}]);

angularApp.controller('EditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.gallery_uuid = galleryUUID;
    $scope.uuid = galleryUUID;
    $scope.name = '';
    $scope.subtitle = '';
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
        $scope.subtitle = gallery.subtitle;
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
            $scope.items[i].position = i + 1;
        }
        $scope.editing = true;
    };
    $scope.removeItem = function(uuid) {
        var item;
        $http.delete('/admin/gallery/item/' + uuid).success(function() {
            var position = -1;
            for (var i = 0; i < $scope.items.length; i++) {
                if ($scope.items[i].uuid == uuid) {
                    position = $scope.items[i].position;
                }
                if (position >= 0) {
                    $scope.items[i].position = i;
                }
            }
            $scope.items.splice(position - 1, 1);
            $scope.updateGallery();
        });
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
          $window.location = "/admin/galleries";
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
                    'subtitle': $scope.subtitle,
                    'author': $scope.author,
                    'cover_photo': $scope.coverPhoto,
                    'items': $scope.items,
                    'published': $scope.published};
        $http.put("/admin/gallery/" + $scope.gallery_uuid, data).success(function(data) {
            $scope.editing = false;
        });
      } else {
        var data = {'name': $scope.name,
                    'subtitle': $scope.subtitle,
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

angularApp.controller('UploadImageController', ['$scope', '$http', '$window', '$sce', '$upload', '$log', function($scope, $http, $window, $sce, $upload, $log) {
  $scope.file = [];
  $scope.dataUrls = [];
  $scope.item = null;
  $scope.error = false;
  $scope.alertMessage = '';
  $scope.loading = false;
  $scope.widthStyle = {"width": "0%"};
  $scope.generatingSizes = false;
  $scope.init = function(imageRoute, item) {
      $scope.imageRoute = imageRoute;
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
      var key = $scope.imageRoute + "/" + fileName;
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
        data = {"image_route": $scope.imageRoute,
                "filename": fileName};
        $http.post('/images/generate_sizes', data).success(function(data) {
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
