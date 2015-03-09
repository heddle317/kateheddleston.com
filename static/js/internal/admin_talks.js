angularApp.controller('AdminTalksController', ['$scope', '$http', '$sce', function($scope, $http, $sce) {
    $scope.loading = true;
    $scope.items = {'published': [], 'unpublished': [], 'archived': []};
    $scope.currentContainer = '.published';
    $http.get('/admin/talks').success(function(response) {
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
        $http.put("/admin/talks/" + $scope.talk.uuid, data).success(function(data) {
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
