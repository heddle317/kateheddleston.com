$(document).ready(function() {
  $('#comment-tooltip').popover({html: true,
                                 viewport: {'selector': 'body', 'padding': 20}});
});

function CommentCtrl($scope, $http, $window, $log) {
  $scope.tooltipContent = "I use Twitter for comments because Twitter is largely a public forum. I don't want comment threads on my website to be a place where people can hide behind anonymity and make cruel remarks. I appreciate all thoughtful, funny, and constructive opinions about the content posted here. If you are not comfortable using Twitter to voice your thoughts then you may reach out to me directly.<br><br><strong>Why do I add the blog post link to the tweet?</strong><br>To shamelessly promote my content of course. Actually, the link is how I find the tweets through Twitter's API to display here."
  $scope.numComments = null;
  $scope.comments = [];
  $scope.getComments = function() {
    $http.get($window.location.pathname + '/comments').success(function(data) {
      $scope.numComments = data.num_comments;
      $scope.comments = data.comments;
      var comment;
      for (var i = 0; i < $scope.comments.length; i++) {
        comment = $scope.comments[i];
        comment.user = JSON.parse(comment.user);
        comment.author = JSON.parse(comment.author);
        var j;
        var link;
        var url;
        for (j = 0; j < comment.entities.urls.length; j++) {
          url = comment.entities.urls[j];
          link = "<a href='" + url.expanded_url + "' target='_blank'>" + url.url + "</a>";
          comment.text = comment.text.replace(url.url, link);
        }
        var mention;
        for (j = 0; j < comment.entities.user_mentions.length; j++) {
          mention = comment.entities.user_mentions[j];
          link = "<a href='https://www.twitter.com/" + mention.screen_name + "' target='_blank'>@" + mention.screen_name + "</a>";
          comment.text = comment.text.replace("@" + mention.screen_name, link);
        }
        var hashtag;
        for (j = 0; j < comment.entities.hashtags.length; j++) {
          hashtag = comment.entities.hashtags[j];
          link = "<a href='https://www.twitter.com/hashtag/" + hashtag.text + "?src=hash' target='_blank'>#" + hashtag.text + "</a>";
          comment.text = comment.text.replace("#" + hashtag.text, link);
        }
      }
    });
  };
  $scope.getComments();
};
