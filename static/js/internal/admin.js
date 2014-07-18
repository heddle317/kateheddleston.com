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
            $scope.talks.push(data);
            $scope.newTitle = '';
            $scope.newDescription = '';
            $scope.newSlidesLink = '';
            $scope.newVideoLink = '';
            $scope.newImageLink = '';
            $scope.newDate = '';
            $scope.newDescriptionLink = '';
            $scope.newLocation = '';
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
    };
    $scope.cancel = function() {
        $scope.editing = false;
    };
    $scope.editTalk = function() {
        $scope.editing = true;
    };
    $scope.updateTalk = function() {
        var data = {'title': $scope.title,
                    'description': $scope.description,
                    'slides_link': $scope.slidesLink,
                    'video_link': $scope.videoLink,
                    'description_link': $scope.descriptionLink,
                    'location': $scope.location,
                    'date': $scope.date,
                    'image_link': $scope.imageLink};
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
        var index;
        for (var i = 0; i < $scope.talks.length; i++) {
            if ($scope.talks[i].uuid == $scope.uuid) {
                index = i;
            }
        }
        $scope.talks.splice(index, 1);
      });
    };
};

function BlogsCtrl($scope, $http) {
    $scope.blogs = [];
    $http.get('/admin/blog_post').success(function(response) {
        $scope.blogs = response;
    });

    $scope.createBlog = function() {
        var data = {'title': $scope.newTitle,
                    'body': $scope.newBody,
                    'image_link': $scope.newImageLink};
        $http.post("/admin/blog_post", data).success(function(data) {
            $scope.blogs.push(data);
            $scope.newTitle = '';
            $scope.newBody = '';
            $scope.newImageLink = '';
        });
    };
};

function BlogCtrl($scope, $http, $window, $sce) {
    $scope.init = function(blog) {
      $scope.uuid = blog.uuid;
      $scope.title = blog.title;
      $scope.body = blog.body;
      $scope.image_link = blog.image_link;
    };
    $scope.editing = false;
    $scope.editPost = function() {
      $scope.editing = true;
    };
    $scope.goToBlog = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/blog/" + $scope.uuid;
        }
    };
    $scope.cancel = function() {
      $scope.editing = false;
    };
    $scope.delete = function() {
      var confirm = $window.confirm("Are you sure you want to delete this blog post?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/blog_post/" + $scope.uuid).success(function(data) {
        var index;
        for (var i = 0; i < $scope.blogs.length; i++) {
            if ($scope.blogs[i].uuid == $scope.uuid) {
                index = i;
            }
        }
        $scope.blogs.splice(index, 1);
      });
    };
    $scope.updatePost = function() {
      var data = {'title': $scope.title,
                  'body': $scope.body,
                  'image_link': $scope.image_link};
      $http.put("/admin/blog_post/" + $scope.uuid, data).success(function(data) {
        $scope.editing = false;
      });
    };
};
