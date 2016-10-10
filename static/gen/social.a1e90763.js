angularApp.controller('SocialController', ['$scope', '$http', '$log', '$window', function($scope, $http, $log, $window) {
    $scope.openPopup = function(url, type) {
        var width  = 575,
        height = 400,
        left   = ($(window).width()  - width)  / 2,
        top    = ($(window).height() - height) / 2,
        opts   = 'status=1' +
        ',width='  + width  +
        ',height=' + height +
        ',top='    + top    +
        ',left='   + left;

        window.open(url, type, opts);
        return false;
    };
    $scope.openFBPopup = function(u, appID) {
        var url = 'https://www.facebook.com/sharer/sharer.php?app_id=' + appID + '&sdk=joey&u=' + u + '&display=popup&ref=plugin&src=share_button';
        $scope.openPopup(url, "facebook");
    };
}]);
