angularApp.controller('AdminTalksController', ['$scope', '$http', '$sce', function($scope, $http, $sce) {
    $scope.loading = true;
    $scope.items = {'published': [], 'unpublished': [], 'archived': []};
    $scope.currentContainer = '.unpublished';
    $http.get('/admin/api/talks').success(function(response) {
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
            var msnry = new Masonry($scope.currentContainer, {columnWidth: 125,
                                                              itemSelector: ".item",
                                                              gutter: 10,
                                                              isFitWidth: true,
                                                              transitionDuration: 0});
        });
    };
}]);

angularApp.controller('MiniEditTalkController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.initTalk = function(talk) {
        $scope.talk = talk;
    };
    $scope.publishTalk = function(publish) {
        $scope.talk.published = publish;
        $scope.talk.archived = false;
        $scope.updateTalk();
    };
    $scope.archiveTalk = function(archive) {
        $scope.talk.archived = archive;
        $scope.updateTalk();
    };
    $scope.updateTalk = function() {
        $scope.removeItem($scope.talk.uuid);
        if ($scope.talk.published) {
            $scope.items.published.push($scope.talk);
        } else if ($scope.talk.archived) {
            $scope.items.archived.push($scope.talk);
        } else {
            $scope.items.unpublished.push($scope.talk);
        }
        $scope.sortLists();
        var data = {'published': $scope.talk.published,
                    'archived': $scope.talk.archived};
        $http.put("/admin/api/talks/" + $scope.talk.uuid, data).success(function(data) {
        });
    };
}]);

angularApp.controller('EditTalkController', ['$scope', '$http', '$log', '$window', '$sce', function($scope, $http, $log, $window, $sce) {
    $scope.editing = false;
    $scope.talk = null;
    $scope.initTalk = function(talk) {
        $scope.talk = talk;
        $scope.talk_uuid = talk.uuid;
        if (!$scope.talk_uuid) {
            $scope.editing = true;
        }
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
    if (talkUUID) {
        $http.get('/admin/api/talks/' + talkUUID).success(function(response) {
            $scope.initTalk(response);
        });
    } else {
        $http.get('/admin/api/talks').success(function(response) {
            $scope.initTalk(response);
        });
    }
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
                    'image_name': $scope.talk.image_name};
        if ($scope.talk_uuid) {
            data['published'] = $scope.published;
            $http.put("/admin/api/talks/" + $scope.talk_uuid, data).success(function(data) {
                $scope.editing = false;
            });
        } else {
            $http.post("/admin/api/talks", data).success(function(data) {
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
      $http.delete("/admin/api/talks/" + $scope.talk_uuid).success(function(data) {
          $window.location = "/admin/talks";
      });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
}]);

angularApp.controller('UploadImageController', ['$scope', '$http', '$window', '$sce', '$upload', '$log', function($scope, $http, $window, $sce, $upload, $log) {
    $scope.file = [];
    $scope.dataUrls = [];
    $scope.error = false;
    $scope.alertMessage = '';
    $scope.loading = false;
    $scope.widthStyle = {"width": "0%"};
    $scope.generatingSizes = false;
    $scope.imageRoute = 'talks/' + talkUUID;
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
                $scope.talk.image_name = fileName;
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
