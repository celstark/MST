global order
global orderLag

numgood=0;
tries=10000;
combined_order=zeros(320,1);
combined_lag=zeros(320,1);

for i=1:tries
    %good = CreateOrder_AllShort();
    good = CreateOrder_80();
    
    if good
        %csvwrite(sprintf('order_80_%d.txt',numgood),[order orderLag])
        numgood=numgood+1;
        fprintf(1,'%d good entries, inserting from %d - %d\n',numgood,80*(numgood-1)+1,80*numgood);
        combined_lag( (80*(numgood-1) + 1):(80*numgood) ) = orderLag;
        % We need to offset the lure-counts by 25*(block-1) and repeat
        % counts by 15*(block-1). Here block = numgood
        % There are no foils so we can just treat the 2 groups with <= and >
        offset_order=order;
        offset_order(offset_order<=200) = offset_order(offset_order<=200) + (numgood-1)* 15;  % targets
        offset_order(offset_order>200) = offset_order(offset_order>200) + (numgood-1)* 25;  % lures
        combined_order( (80*(numgood-1)+1):(80*numgood) ) = offset_order;
    end
    
    if numgood == 4
         break
    end
end
csvwrite('Eichorder80x4_3.txt',[order orderLag])
numgood/tries
