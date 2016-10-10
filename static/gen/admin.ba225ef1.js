var angularApp = angular.module('angularApp', ['ngResource', 'ngSanitize', 'angularFileUpload']);

angularApp.config(function ($interpolateProvider, $httpProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
    $httpProvider.defaults.headers.post['X-CSRFToken'] = csrftoken;
    $httpProvider.defaults.headers.common['X-CSRFToken'] = $httpProvider.defaults.headers.post['X-CSRFToken'];
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

angularApp.controller('SocialAuthController', ['$scope', '$http', '$window', function($scope, $http, $window) {
    $scope.FBAuth = function() {
        $window.location = "/admin/auth/facebook";
    };
}]);
