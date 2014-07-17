function TalksCtrl($scope, $http, $sce) {
    $scope.talks = [];
    $http.get('/admin/talks').success(function(data) {
        $scope.talks = data;
    });

    $scope.createTalk = function() {
        var data = {'title': $scope.title,
                    'description': $scope.description,
                    'slides_link': $scope.slidesLink,
                    'video_link': $scope.videoLink,
                    'description_link': $scope.descriptionLink,
                    'location': $scope.location,
                    'date': $scope.date,
                    'image_link': $scope.imageLink};
        $http.post("/admin/talks", data).success(function(data) {
            $scope.talks.push(data);
            $scope.title = '';
            $scope.description = '';
            $scope.slidesLink = '';
            $scope.videoLink = '';
            $scope.imageLink = '';
            $scope.date = '';
            $scope.descriptionLink = '';
            $scope.location = '';
        });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
};

function BlogsCtrl($scope, $http, $sce) {
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
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
};

function BlogCtrl($scope, $http, $window) {
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
