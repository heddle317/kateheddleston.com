function TalksCtrl($scope, $http) {
    $scope.todos = [
        {text:'learn angular', done:true},
        {text:'build an angular app', done:false}];
    $scope.talks = [];
    $http.get('/admin/talks').success(function(data) {
        console.log(data);
        $scope.talks = data;
    });

    $scope.createTalk = function() {
        if (!$scope.title) {
            return;
        }
        if (!$scope.description) {
            return;
        }
        if (!$scope.slidesLink) {
            return;
        }
        if (!$scope.videoLink) {
            return;
        }
        if (!$scope.imageLink) {
            return;
        }
        if (!$scope.location) {
            return;
        }
        if (!$scope.date) {
            return;
        }
        if (!$scope.descriptionLink) {
            return;
        }
        var data = {'title': $scope.title,
                    'description': $scope.description,
                    'slides_link': $scope.slidesLink,
                    'video_link': $scope.videoLink,
                    'description_link': $scope.descriptionLink,
                    'location': $scope.location,
                    'date': $scope.date,
                    'image_link': $scope.imageLink};
        $http.post("/admin/talks", data).success(function(data) {
            console.log(data);
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
}
