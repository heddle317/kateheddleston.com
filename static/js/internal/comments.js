angularApp.controller('CommentController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
  $scope.numComments = null;
  $scope.comments = [];
  $scope.rows = function() {
      var rows = Math.ceil($scope.comments.length / 4);
      var row_array = new Array();
      for (var i = 0; i < rows + 1; i++) {
          row_array.push(i);
      }
      return row_array;
  };
  $scope.getRowComments = function(row) {
      var comment_array = new Array();
      var start_index = row * 4;
      var end_index = start_index + 4;
      var index = start_index;
      while (index < end_index) {
        if (index < $scope.comments.length) {
            comment_array.push($scope.comments[index]);
        }
        index = index + 1;
      }
      return comment_array;
  };
  $scope.getComments = function() {
    $http.get('/blog/' + galleryUUID + '/comments').success(function(data) {
      $scope.numComments = data.num_comments;
      $scope.comments = data.comments;
      var comment;
      for (var i = 0; i < $scope.comments.length; i++) {
        comment = $scope.comments[i];
        var j;
        var link;
        var url;
        if (comment.entities.urls) {
            for (j = 0; j < comment.entities.urls.length; j++) {
                url = comment.entities.urls[j];
                link = "<a href='" + url.expanded_url + "' target='_blank'>" + url.url + "</a>";
                comment.text = comment.text.replace(url.url, link);
            }
        }
        var media;
        if (comment.entities.media) {
          for (j = 0; j < comment.entities.media.length; j++) {
            media = comment.entities.media[j];
            link = "<a href='" + media.expanded_url + "' target='_blank'>" + media.url + "</a>";
            comment.text = comment.text.replace(media.url, link);
          }
        }
        var mention;
        if (comment.entities.user_mentions) {
            for (j = 0; j < comment.entities.user_mentions.length; j++) {
                mention = comment.entities.user_mentions[j];
                link = "<a href='https://www.twitter.com/" + mention.screen_name + "' target='_blank'>@" + mention.screen_name + "</a>";
                comment.text = comment.text.replace("@" + mention.screen_name, link);
            }
        }
        var hashtag;
        if (comment.entities.hashtags) {
            for (j = 0; j < comment.entities.hashtags.length; j++) {
                hashtag = comment.entities.hashtags[j];
                link = "<a href='https://www.twitter.com/hashtag/" + hashtag.text + "?src=hash' target='_blank'>#" + hashtag.text + "</a>";
                comment.text = comment.text.replace("#" + hashtag.text, link);
            }
        }
      }
    });
  };
  $scope.getComments();
}]);
