function plotBar2(a, b, name, name_pre)
	if(nargin<4)
		name='try';
		name_pre='try';
	end

	if(length(a) < length(b))
		a = [a transpose(zeros(length(b)-length(a), 1))];
	else
		b = [b transpose(zeros(length(a)-length(b), 1))];
	end
	
	f = figure();

	to = length(a)
	bar(1:to, a, 'r');
	hold on;
	from = length(a)+1;
	to = length(a)+length(b)
	bar(from:to, b, 'b');
	set(gca,'xticklabel',{});

	figure_file = strcat('../data/charts/', name_pre, '_', name, '.png');
	figure_file = char(figure_file);
	saveas(f, figure_file, 'png');

	figure_file = strcat('../data/charts/', name_pre, '_', name, '.fig');
	figure_file = char(figure_file);
	saveas(f, figure_file, 'fig');