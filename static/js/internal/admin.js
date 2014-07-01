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
    $http.get('/admin/blog_post').success(function(data) {
        $scope.blogs = data;
    });

    $scope.createBlog = function() {
        var data = {'title': $scope.title,
                    'body': $scope.body,
                    'image_link': $scope.imageLink};
        $http.post("/admin/blog_post", data).success(function(data) {
            $scope.blogs.push(data);
            $scope.title = '';
            $scope.body = '';
            $scope.imageLink = '';
        });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
};
