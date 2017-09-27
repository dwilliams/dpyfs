import * as gulp from 'gulp';
import * as changed from 'gulp-changed';
import * as project from '../aurelia.json';

export default function dist() {
  //return gulp.src(project.paths.???)
  //  .pipe(changed(project.paths.output, {extension: '.???'}))
  //  .pipe(gulp.dest(project.paths.output));
  return gulp.src(project.dist.sources, { "base" : "." }).pipe(gulp.dest(project.dist.output));
}

