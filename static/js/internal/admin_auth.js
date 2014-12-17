angularApp.controller('SocialAuthController', ['$scope', '$http', '$window', function($scope, $http, $window) {
    $scope.FBAuth = function() {
        $window.location = "/admin/auth/facebook";
    };
}]);
